#!/usr/bin/env python3
"""Envia eventos de atividade e relatórios de pendências pelo Telegram.

O modo --dry-run valida a política e produz a mensagem sem acessar a rede ou
exigir credenciais. Tokens e chat IDs devem permanecer fora do Git.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable
from urllib import error, parse, request

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "config" / "autonomy" / "telegram_delivery_policy.json"
MAX_MESSAGE_LENGTH = 3900


class ReporterError(RuntimeError):
    """Erro seguro do executor, sem exposição de credenciais."""


def env(name: str) -> str | None:
    value = os.environ.get(name)
    return value.strip() if value and value.strip() else None


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def load_policy(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReporterError(f"Política Telegram não encontrada: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReporterError("Política Telegram contém JSON inválido.") from exc

    if not isinstance(payload, dict) or payload.get("enabled") is not True:
        raise ReporterError("Política Telegram está ausente ou desabilitada.")
    if payload.get("credentials_outside_git") is not True:
        raise ReporterError("A política deve exigir credenciais fora do Git.")
    return payload


def clean_text(value: str, field: str, max_length: int = 1200) -> str:
    text = " ".join(value.strip().split())
    if not text:
        raise ReporterError(f"Campo obrigatório vazio: {field}.")
    if len(text) > max_length:
        raise ReporterError(f"Campo {field} excede {max_length} caracteres.")
    return text


def percent(value: int, field: str) -> int:
    if value < 0 or value > 100:
        raise ReporterError(f"{field} deve estar entre 0 e 100.")
    return value


def truncate_message(message: str) -> str:
    if len(message) <= MAX_MESSAGE_LENGTH:
        return message
    suffix = "\n\n[Mensagem reduzida para o limite seguro do Telegram.]"
    return message[: MAX_MESSAGE_LENGTH - len(suffix)].rstrip() + suffix


def bullet_lines(values: list[str], empty_label: str = "Nenhum informado") -> str:
    cleaned = [" ".join(value.strip().split()) for value in values if value.strip()]
    if not cleaned:
        return f"- {empty_label}"
    return "\n".join(f"- {value}" for value in cleaned)


def validate_policy_event(policy: dict[str, Any], event: str) -> None:
    if event in {"activity_started", "activity_completed"}:
        section = policy.get("activity_notifications") or {}
        if section.get("enabled") is not True or event not in section.get("events", []):
            raise ReporterError(f"Evento {event} não está habilitado na política.")
        return

    if event == "developer_pending_report":
        section = policy.get("developer_pending_reports") or {}
        if section.get("enabled") is not True:
            raise ReporterError("Relatórios de pendências não estão habilitados.")
        return

    raise ReporterError(f"Evento Telegram desconhecido: {event}.")


def build_activity_started(args: argparse.Namespace) -> str:
    difficulty = args.reported_difficulty
    if difficulty < 1 or difficulty > 5:
        raise ReporterError("Dificuldade deve estar entre 1 e 5.")
    progress = percent(args.initial_progress_percent, "Progresso inicial")
    return truncate_message(
        "\n".join(
            [
                "Atividade iniciada",
                f"Nome: {clean_text(args.activity_name, 'activity_name', 200)}",
                f"Descrição técnica: {clean_text(args.technical_description, 'technical_description')}",
                f"Tempo estimado: {clean_text(args.estimated_completion_time, 'estimated_completion_time', 120)}",
                f"Dificuldade: {difficulty}/5",
                f"Progresso inicial: {progress}%",
                f"Registrado em: {now_iso()}",
            ]
        )
    )


def build_activity_completed(args: argparse.Namespace) -> str:
    progress = percent(args.completion_percent, "Percentual de conclusão")
    failure_detected = bool(args.failure_detected)
    failure_summary = clean_text(
        args.failure_summary or "Não se aplica", "failure_summary"
    )
    failure_cause = clean_text(args.failure_cause or "Não se aplica", "failure_cause")
    resolution_action = clean_text(
        args.resolution_action or "Nenhuma ação adicional registrada",
        "resolution_action",
    )
    resolvable = clean_text(args.resolvable or "Não informado", "resolvable", 120)

    return truncate_message(
        "\n".join(
            [
                "Atividade concluída",
                f"Nome: {clean_text(args.activity_name, 'activity_name', 200)}",
                f"Status: {args.status}",
                f"Conclusão: {progress}%",
                f"Falha detectada: {'sim' if failure_detected else 'não'}",
                f"Resumo da falha: {failure_summary}",
                f"Causa: {failure_cause}",
                f"Ação de resolução: {resolution_action}",
                f"Pode ser resolvida: {resolvable}",
                "Pendências:",
                bullet_lines(args.pending_item),
                "Próximos passos:",
                bullet_lines(args.next_step),
                f"Registrado em: {now_iso()}",
            ]
        )
    )


def build_pending_report(args: argparse.Namespace) -> str:
    if args.report_index not in {1, 2, 3, 4}:
        raise ReporterError("report_index deve estar entre 1 e 4.")
    generated_at = args.generated_at or now_iso()
    return truncate_message(
        "\n".join(
            [
                f"Relatório de pendências {args.report_index}/4",
                f"Gerado em: {clean_text(generated_at, 'generated_at', 120)}",
                "Pendências abertas:",
                bullet_lines(args.open_pending),
                "Pendências bloqueadas:",
                bullet_lines(args.blocked_pending),
                f"Resumo de risco: {clean_text(args.risk_summary, 'risk_summary')}",
                f"Resumo de prazo: {clean_text(args.eta_summary, 'eta_summary')}",
            ]
        )
    )


def send_message(
    token: str,
    chat_id: str,
    message: str,
    *,
    timeout: int = 20,
    retries: int = 3,
    urlopen: Callable[..., Any] | None = None,
    sleeper: Callable[[float], None] | None = None,
) -> None:
    if retries < 1 or retries > 5:
        raise ReporterError("retries deve estar entre 1 e 5.")
    if timeout < 1 or timeout > 120:
        raise ReporterError("timeout deve estar entre 1 e 120 segundos.")

    open_url = urlopen or request.urlopen
    sleep = sleeper or time.sleep
    data = parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
    req = request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    last_error = "falha desconhecida"
    for attempt in range(1, retries + 1):
        try:
            with open_url(req, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                status = int(getattr(response, "status", 200))
                if status not in range(200, 300) or payload.get("ok") is not True:
                    raise ReporterError("Telegram recusou a mensagem.")
                return
        except ReporterError:
            raise
        except error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            if 400 <= exc.code < 500 and exc.code != 429:
                break
        except (error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            last_error = exc.__class__.__name__

        if attempt < retries:
            sleep(min(2 ** (attempt - 1), 8))

    raise ReporterError(
        f"Falha ao enviar ao Telegram após {retries} tentativa(s): {last_error}."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--telegram-token", default=env("TELEGRAM_BOT_TOKEN"))
    parser.add_argument("--telegram-chat-id", default=env("TELEGRAM_CHAT_ID"))
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--retries", type=int, default=3)

    sub = parser.add_subparsers(dest="command", required=True)

    started = sub.add_parser("activity-started")
    started.add_argument("--activity-name", required=True)
    started.add_argument("--technical-description", required=True)
    started.add_argument("--estimated-completion-time", required=True)
    started.add_argument("--reported-difficulty", type=int, required=True)
    started.add_argument("--initial-progress-percent", type=int, default=0)

    completed = sub.add_parser("activity-completed")
    completed.add_argument("--activity-name", required=True)
    completed.add_argument(
        "--status", choices=("success", "partial_success", "failed"), required=True
    )
    completed.add_argument("--completion-percent", type=int, required=True)
    completed.add_argument("--failure-detected", action="store_true")
    completed.add_argument("--failure-summary")
    completed.add_argument("--failure-cause")
    completed.add_argument("--resolution-action")
    completed.add_argument("--resolvable")
    completed.add_argument("--pending-item", action="append", default=[])
    completed.add_argument("--next-step", action="append", default=[])

    report = sub.add_parser("pending-report")
    report.add_argument("--report-index", type=int, required=True)
    report.add_argument("--generated-at")
    report.add_argument("--open-pending", action="append", default=[])
    report.add_argument("--blocked-pending", action="append", default=[])
    report.add_argument("--risk-summary", required=True)
    report.add_argument("--eta-summary", required=True)

    return parser


def render_event(args: argparse.Namespace, policy: dict[str, Any]) -> tuple[str, str]:
    if args.command == "activity-started":
        event = "activity_started"
        message = build_activity_started(args)
    elif args.command == "activity-completed":
        event = "activity_completed"
        message = build_activity_completed(args)
    elif args.command == "pending-report":
        event = "developer_pending_report"
        message = build_pending_report(args)
    else:
        raise ReporterError(f"Comando desconhecido: {args.command}.")

    validate_policy_event(policy, event)
    return event, message


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    try:
        policy_path = Path(args.policy).expanduser().resolve()
        policy = load_policy(policy_path)
        event, message = render_event(args, policy)

        if args.dry_run:
            print(
                json.dumps(
                    {
                        "event": event,
                        "message": message,
                        "policy_version": policy.get("version"),
                        "sent": False,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0

        if not args.telegram_token or not args.telegram_chat_id:
            raise ReporterError(
                "Envio real exige TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID fora do Git."
            )

        send_message(
            args.telegram_token,
            args.telegram_chat_id,
            message,
            timeout=args.timeout,
            retries=args.retries,
        )
    except ReporterError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2

    print(f"Evento {event} enviado com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
