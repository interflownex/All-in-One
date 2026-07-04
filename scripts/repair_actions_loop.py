from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INTERVAL_SECONDS = 300
DEFAULT_GIT_ACTIVITY = "loop infinito GitHub Actions"
DEFAULT_BRANCH_RUN_LIMIT = 50
DEFAULT_PYTEST_TARGETS = (
    "tests/test_runtime_event_generation.py",
    "tests/test_outbox_dispatcher_runtime_events.py",
    "tests/test_postgres_stores_matrix.py",
    "tests/test_security_gates.py",
)
DEFAULT_REPAIR_BUNDLE = (
    ("{python}", "scripts/scaffold_modules.py"),
    ("{python}", "scripts/generate_domain_event_fixtures.py"),
    ("{python}", "scripts/check_generated_artifacts.py"),
    ("{python}", "scripts/validate_openapi.py"),
    ("{python}", "scripts/validate_repository.py"),
    ("{python}", "-m", "pytest", "-q", *DEFAULT_PYTEST_TARGETS),
)
FAILURE_WORDS = {
    "fail",
    "failed",
    "failure",
    "error",
    "errored",
    "cancelled",
    "canceled",
    "timed_out",
}
SUCCESS_WORDS = {
    "pass",
    "passed",
    "success",
    "succeeded",
    "skipped",
    "neutral",
}


@dataclass(frozen=True)
class FailureRecord:
    name: str
    status: str
    details_url: str | None
    run_id: str | None
    source: str
    snippet: str | None = None


def run_command(
    command: Sequence[str],
    *,
    cwd: Path = ROOT,
    check: bool = True,
    print_on_failure: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(command),
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0 and print_on_failure:
        print(f"$ {shlex.join(command)}", file=sys.stderr)
        if result.stdout:
            print(result.stdout.rstrip(), file=sys.stderr)
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            list(command),
            output=result.stdout,
            stderr=result.stderr,
        )
    return result


def repo_root() -> Path:
    result = run_command(["git", "rev-parse", "--show-toplevel"])
    root = result.stdout.strip()
    if not root:
        raise RuntimeError("Nao foi possivel identificar a raiz do repositorio.")
    return Path(root)


def git_config_value(key: str) -> str:
    result = run_command(["git", "config", "--get", key], check=False, print_on_failure=False)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def git_remote_names() -> list[str]:
    result = run_command(["git", "remote"], check=True, print_on_failure=False)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def ensure_git_identity() -> None:
    if not git_config_value("user.name"):
        run_command(["git", "config", "user.name", "all-in-one-bot"], check=True, print_on_failure=False)
    if not git_config_value("user.email"):
        run_command(
            ["git", "config", "user.email", "actions@users.noreply.github.com"],
            check=True,
            print_on_failure=False,
        )


def current_branch() -> str:
    result = run_command(["git", "branch", "--show-current"], check=False, print_on_failure=False)
    branch = result.stdout.strip()
    if branch:
        return branch
    if "GITHUB_REF_NAME" in os.environ:
        return os.environ["GITHUB_REF_NAME"]
    return "main"


def ensure_workspace_ready(branch: str) -> None:
    run_command(
        [
            sys.executable,
            "scripts/multi_agent_sync_guard.py",
            "preflight",
            "--branch",
            branch,
            "--remotes",
            "origin",
            "fork",
            "--integrate",
        ]
    )


def choose_push_remote(branch: str) -> str:
    available = set(git_remote_names())
    for key in (
        git_config_value(f"branch.{branch}.pushRemote"),
        git_config_value("remote.pushDefault"),
        git_config_value(f"branch.{branch}.remote"),
        "fork",
        "origin",
    ):
        if key and key in available:
            return key
    if available:
        return sorted(available)[0]
    raise RuntimeError("Nenhum remoto Git configurado para sincronizacao.")


def is_failure_state(value: object) -> bool:
    normalized = str(value or "").strip().lower()
    if not normalized:
        return False
    if normalized in SUCCESS_WORDS:
        return False
    return any(word in normalized for word in FAILURE_WORDS)


def parse_timestamp(value: object) -> datetime:
    text = str(value or "").strip()
    if not text:
        return datetime.min.replace(tzinfo=UTC)
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def extract_run_id(url: str | None) -> str | None:
    if not url:
        return None
    marker = "/actions/runs/"
    if marker not in url:
        return None
    suffix = url.split(marker, 1)[1]
    return suffix.split("/", 1)[0]


def trim_log_snippet(text: str, limit: int = 60) -> str:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    for index, line in enumerate(lines):
        if any(marker in line for marker in ("ERROR", "Traceback", "##[error]", "ModuleNotFoundError")):
            start = max(0, index - 4)
            end = min(len(lines), index + limit)
            return "\n".join(lines[start:end])
    return "\n".join(lines[-limit:])


def latest_workflow_runs(runs: Iterable[Mapping[str, object]]) -> list[Mapping[str, object]]:
    latest: dict[str, Mapping[str, object]] = {}
    for run in runs:
        workflow_name = str(run.get("workflowName") or run.get("name") or "").strip()
        if not workflow_name:
            continue
        current = latest.get(workflow_name)
        if current is None or parse_timestamp(run.get("createdAt")) > parse_timestamp(current.get("createdAt")):
            latest[workflow_name] = run
    return sorted(latest.values(), key=lambda item: parse_timestamp(item.get("createdAt")), reverse=True)


def current_workflow_failures(runs: Iterable[Mapping[str, object]]) -> list[Mapping[str, object]]:
    failures: list[Mapping[str, object]] = []
    for run in latest_workflow_runs(runs):
        conclusion = run.get("conclusion")
        status = run.get("status")
        if is_failure_state(conclusion) or (
            conclusion is None and is_failure_state(status) and str(status).strip().lower() not in {"queued", "in_progress", "completed"}
        ):
            failures.append(run)
    return failures


def parse_pr_checks(raw_output: str) -> list[Mapping[str, object]]:
    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError:
        payload = None

    if isinstance(payload, list):
        return payload

    records: list[Mapping[str, object]] = []
    for line in raw_output.splitlines():
        if not line.strip():
            continue
        columns = [part.strip() for part in line.split("\t") if part.strip()]
        if len(columns) < 2:
            continue
        name = columns[0]
        status = columns[1]
        details_url = columns[-1] if columns[-1].startswith("http") else None
        records.append(
            {
                "name": name,
                "state": status,
                "bucket": status,
                "link": details_url,
                "detailsUrl": details_url,
                "workflow": None,
            }
        )
    return records


def inspect_pr_failures(pr_ref: str) -> list[FailureRecord]:
    result = run_command(
        [
            "gh",
            "pr",
            "checks",
            pr_ref,
            "--json",
            "name,state,bucket,link,detailsUrl,workflow",
        ],
        check=False,
        print_on_failure=False,
    )
    raw_output = result.stdout if result.returncode == 0 and result.stdout.strip() else ""
    if not raw_output:
        fallback = run_command(["gh", "pr", "checks", pr_ref], check=False, print_on_failure=False)
        raw_output = fallback.stdout
    records = parse_pr_checks(raw_output)
    failures: list[FailureRecord] = []
    for record in records:
        state = str(record.get("state") or "")
        bucket = str(record.get("bucket") or "")
        if not is_failure_state(state) and not is_failure_state(bucket):
            continue
        details_url = str(record.get("detailsUrl") or record.get("link") or "") or None
        failures.append(
            FailureRecord(
                name=str(record.get("name") or "checagem desconhecida"),
                status=state or bucket or "failure",
                details_url=details_url,
                run_id=extract_run_id(details_url),
                source="pr",
            )
        )
    return failures


def inspect_branch_failures(branch: str, limit: int = DEFAULT_BRANCH_RUN_LIMIT) -> list[FailureRecord]:
    result = run_command(
        [
            "gh",
            "run",
            "list",
            "--branch",
            branch,
            "--limit",
            str(limit),
            "--json",
            "databaseId,workflowName,status,conclusion,createdAt,url,event,headBranch",
        ],
        check=False,
        print_on_failure=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    failures: list[FailureRecord] = []
    for run in current_workflow_failures(payload):
        workflow_name = str(run.get("workflowName") or "workflow desconhecido")
        details_url = str(run.get("url") or "") or None
        failures.append(
            FailureRecord(
                name=workflow_name,
                status=str(run.get("conclusion") or run.get("status") or "failure"),
                details_url=details_url,
                run_id=str(run.get("databaseId") or extract_run_id(details_url) or ""),
                source="branch",
            )
        )
    return failures


def capture_failure_snippets(failures: Sequence[FailureRecord]) -> list[FailureRecord]:
    captured: list[FailureRecord] = []
    for failure in failures:
        run_id = failure.run_id or extract_run_id(failure.details_url)
        if not run_id:
            captured.append(failure)
            continue
        result = run_command(
            ["gh", "run", "view", run_id, "--log-failed"],
            check=False,
            print_on_failure=False,
        )
        snippet = trim_log_snippet(result.stdout) if result.stdout else None
        captured.append(
            FailureRecord(
                name=failure.name,
                status=failure.status,
                details_url=failure.details_url,
                run_id=run_id,
                source=failure.source,
                snippet=snippet,
            )
        )
    return captured


def build_repair_bundle(python_executable: str) -> tuple[tuple[str, ...], ...]:
    bundle: list[tuple[str, ...]] = []
    for command in DEFAULT_REPAIR_BUNDLE:
        rendered = tuple(part.format(python=python_executable) for part in command)
        bundle.append(rendered)
    return tuple(bundle)


def git_status_lines() -> list[str]:
    result = run_command(["git", "status", "--porcelain", "--untracked-files=all"], check=True, print_on_failure=False)
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def has_cached_changes() -> bool:
    result = run_command(["git", "diff", "--cached", "--quiet"], check=False, print_on_failure=False)
    return result.returncode != 0


def sync_worktree(activity: str, branch: str) -> bool:
    if not git_status_lines():
        return False
    ensure_git_identity()
    try:
        run_command(["git", "add", "-A"])
        if not has_cached_changes():
            return False
        run_command(["git", "diff", "--cached", "--check"])
        remote = choose_push_remote(branch)
        commit_message = f"chore(auto-repair): {activity}".strip()
        commit_body = f"Sincronizacao automatica do loop de repair em {datetime.now(UTC).isoformat()}."
        run_command(["git", "commit", "-m", commit_message, "-m", commit_body])
        try:
            run_command(["git", "push", remote, f"HEAD:{branch}"])
        except subprocess.CalledProcessError:
            run_command(
                [
                    sys.executable,
                    "scripts/multi_agent_sync_guard.py",
                    "preflight",
                    "--branch",
                    branch,
                    "--remotes",
                    remote,
                    "origin",
                    "fork",
                    "--integrate",
                ],
                check=False,
            )
            run_command(["git", "push", remote, f"HEAD:{branch}"])
        return True
    except subprocess.CalledProcessError:
        return False


def resolve_target(branch: str, explicit_pr: str | None) -> tuple[str, str]:
    if explicit_pr:
        return "pr", explicit_pr
    result = run_command(
        ["gh", "pr", "view", "--json", "number,url,headRefName,baseRefName,state"],
        check=False,
        print_on_failure=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict) and payload.get("number"):
            return "pr", str(payload["number"])
    return "branch", branch


def inspect_target_failures(target_kind: str, target_value: str) -> list[FailureRecord]:
    if target_kind == "pr":
        return inspect_pr_failures(target_value)
    return inspect_branch_failures(target_value)


def print_failure_summary(failures: Sequence[FailureRecord]) -> None:
    if not failures:
        print("Nenhuma falha ativa encontrada.")
        return
    print("Falhas ativas detectadas:")
    for failure in failures:
        print(f"- {failure.name} [{failure.source}] -> {failure.status}")
        if failure.details_url:
            print(f"  URL: {failure.details_url}")
        if failure.snippet:
            print("  Trecho do log:")
            for line in failure.snippet.splitlines():
                print(f"    {line}")


def run_repair_bundle(python_executable: str) -> tuple[list[tuple[str, ...]], list[tuple[tuple[str, ...], int]]]:
    bundle = build_repair_bundle(python_executable)
    failures: list[tuple[tuple[str, ...], int]] = []
    for command in bundle:
        print(f"Executando reparo: {shlex.join(command)}")
        result = run_command(command, check=False, print_on_failure=True)
        if result.returncode != 0:
            failures.append((command, result.returncode))
    return list(bundle), failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Loop infinito de repair para GitHub Actions e sync Git.")
    parser.add_argument("--pr", help="Numero ou URL da PR a inspecionar. Se omitido, usa a PR da branch atual.")
    parser.add_argument("--branch", default="", help="Branch local a monitorar. Se omitida, usa a branch atual.")
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=DEFAULT_INTERVAL_SECONDS,
        help="Pausa entre ciclos quando --continuous estiver habilitado.",
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Mantem o loop rodando indefinidamente ate interrupcao manual.",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=0,
        help="Limite opcional de ciclos. Zero significa sem limite.",
    )
    parser.add_argument(
        "--activity",
        default=DEFAULT_GIT_ACTIVITY,
        help="Descricao usada no commit automatico do sync.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    os.chdir(root)
    branch = args.branch.strip() or current_branch()
    target_kind, target_value = resolve_target(branch, args.pr.strip() if args.pr else None)

    python_executable = sys.executable
    cycles = 0
    try:
        while True:
            cycles += 1
            print(f"\nCiclo {cycles} | branch={branch} | alvo={target_kind}:{target_value}")
            preflight_ok = True
            try:
                ensure_workspace_ready(branch)
            except subprocess.CalledProcessError:
                preflight_ok = False
                print("Aviso: o preflight multiagente nao ficou pronto neste ciclo.", file=sys.stderr)
            failures = capture_failure_snippets(inspect_target_failures(target_kind, target_value))
            print_failure_summary(failures)

            local_failures: list[tuple[tuple[str, ...], int]] = []
            changed = False
            if preflight_ok:
                _, local_failures = run_repair_bundle(python_executable)
                if local_failures:
                    print("Falhas locais no bundle de reparo:")
                    for command, code in local_failures:
                        print(f"- {shlex.join(command)} -> codigo {code}")
                changed = sync_worktree(args.activity, branch)
                if changed:
                    print("Sincronizacao automatica concluida com commit e push.")
                else:
                    print("Nenhuma alteracao precisou ser sincronizada.")
            else:
                print("Reparo local e sincronizacao pausados ate o preflight ficar pronto.")

            refreshed_failures = capture_failure_snippets(inspect_target_failures(target_kind, target_value))
            if refreshed_failures:
                print("Falhas ainda ativas apos o reparo; o loop continuara.")
                print_failure_summary(refreshed_failures)
            else:
                print("Estado remoto sem falhas ativas.")

            if not args.continuous and args.max_cycles == 0:
                break
            if args.max_cycles > 0 and cycles >= args.max_cycles:
                break
            if args.continuous:
                time.sleep(max(0, args.interval_seconds))
    finally:
        run_command(
            [
                sys.executable,
                "scripts/multi_agent_sync_guard.py",
                "release",
                "--agent",
                "repair-actions-loop",
            ],
            check=False,
            print_on_failure=False,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
