from __future__ import annotations

import argparse
import http.client
import json
import os
import sys
import urllib.parse
import urllib.request
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "config" / "cloudflare" / "mcp_dns_plan.json"
WORKSPACE_PROFILE_PATH = ROOT / "config" / "cloudflare" / "workspace_profile.json"
API_HOST = "api.cloudflare.com"
API_PREFIX = "/client/v4"
ALLOWED_ZONE = "brasildesconto.com.br"
ALLOWED_RECORD_TYPES = {"CNAME"}


class ConfigurationError(RuntimeError):
    """Raised when the declarative DNS plan is unsafe or incomplete."""


class CloudflareAPIError(RuntimeError):
    """Raised when the Cloudflare API rejects a request."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigurationError(f"arquivo ausente: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"JSON inválido em {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"{path} deve conter um objeto JSON")
    return data


def load_plan() -> dict[str, Any]:
    plan = load_json(PLAN_PATH)
    validate_plan(plan)
    return plan


def validate_plan(plan: Mapping[str, Any]) -> None:
    zone = str(plan.get("zone_name", "")).strip().casefold()
    if zone != ALLOWED_ZONE:
        raise ConfigurationError(
            f"zona não autorizada: {zone or '<vazia>'}; esperado {ALLOWED_ZONE}"
        )

    guardrails = plan.get("guardrails")
    if not isinstance(guardrails, Mapping):
        raise ConfigurationError("guardrails ausentes")
    if guardrails.get("allow_apex_changes") is not False:
        raise ConfigurationError("alteração do domínio raiz deve permanecer bloqueada")
    if guardrails.get("allow_wildcards") is not False:
        raise ConfigurationError("wildcards devem permanecer bloqueados")
    if guardrails.get("allow_delete") is not False:
        raise ConfigurationError("remoção de registros deve permanecer bloqueada")

    records = list(iter_plan_records(plan, environment=None, require_targets=False))
    if not records:
        raise ConfigurationError("plano DNS MCP não contém registros")

    seen: set[str] = set()
    canonical = str(
        cast_mapping(plan.get("canonical"), "canonical").get("hostname", "")
    ).casefold()
    if canonical != f"mcp.{ALLOWED_ZONE}":
        raise ConfigurationError(
            f"hostname canônico inválido: {canonical or '<vazio>'}"
        )

    for record in records:
        name = record["name"].casefold()
        record_type = record["type"].upper()
        if name in seen:
            raise ConfigurationError(f"hostname duplicado no plano: {name}")
        seen.add(name)
        _validate_hostname(name)
        if record_type not in ALLOWED_RECORD_TYPES:
            raise ConfigurationError(
                f"tipo de registro não autorizado para {name}: {record_type}"
            )
        if record.get("proxied") is not True:
            raise ConfigurationError(f"registro MCP deve ser proxied: {name}")
        content = record.get("content")
        if content:
            _validate_target(str(content), name)

    serialized = json.dumps(plan, sort_keys=True)
    for marker in ("BEGIN ", "AQ.", "-----", "sk-", "token="):
        if marker in serialized:
            raise ConfigurationError(
                f"plano contém possível material sensível: {marker}"
            )


def cast_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ConfigurationError(f"{name} deve ser um objeto")
    return value


def _validate_hostname(hostname: str) -> None:
    if hostname == ALLOWED_ZONE:
        raise ConfigurationError("alteração do domínio raiz é proibida")
    if "*" in hostname:
        raise ConfigurationError(f"wildcard proibido: {hostname}")
    if not hostname.endswith(f".{ALLOWED_ZONE}"):
        raise ConfigurationError(f"hostname fora da zona permitida: {hostname}")
    labels = hostname.split(".")
    if any(not label or len(label) > 63 for label in labels):
        raise ConfigurationError(f"hostname inválido: {hostname}")


def _validate_target(target: str, record_name: str) -> None:
    normalized = target.strip().casefold().rstrip(".")
    if not normalized:
        raise ConfigurationError(f"target vazio para {record_name}")
    if "://" in normalized or "/" in normalized or " " in normalized:
        raise ConfigurationError(
            f"target CNAME deve ser apenas hostname para {record_name}"
        )
    if normalized == record_name.casefold().rstrip("."):
        raise ConfigurationError(f"CNAME circular para {record_name}")


def iter_plan_records(
    plan: Mapping[str, Any],
    *,
    environment: str | None,
    require_targets: bool,
) -> Iterable[dict[str, Any]]:
    canonical = cast_mapping(plan.get("canonical"), "canonical")
    canonical_environment = str(canonical.get("environment", "production"))
    if environment in (None, canonical_environment):
        yield _record_from_target_env(canonical, require_targets=require_targets)

    environments = plan.get("environments", [])
    if not isinstance(environments, list):
        raise ConfigurationError("environments deve ser uma lista")
    for item in environments:
        config = cast_mapping(item, "environment item")
        if environment is None or config.get("environment") == environment:
            yield _record_from_target_env(config, require_targets=require_targets)

    aliases = plan.get("aliases", [])
    if not isinstance(aliases, list):
        raise ConfigurationError("aliases deve ser uma lista")
    for item in aliases:
        config = cast_mapping(item, "alias item")
        if environment is not None and config.get("environment") != environment:
            continue
        target = str(config.get("target", "")).strip().rstrip(".")
        if not target:
            raise ConfigurationError(
                f"alias sem target: {config.get('hostname', '<desconhecido>')}"
            )
        yield {
            "name": str(config.get("hostname", "")).strip().rstrip("."),
            "type": str(config.get("record_type", "CNAME")).upper(),
            "content": target,
            "proxied": bool(config.get("proxied", True)),
            "ttl": int(config.get("ttl", 1)),
            "comment": "All-in-One MCP alias gerenciado declarativamente",
        }


def _record_from_target_env(
    config: Mapping[str, Any],
    *,
    require_targets: bool,
) -> dict[str, Any]:
    env_name = str(config.get("target_env_var", "")).strip()
    target = os.getenv(env_name, "").strip().rstrip(".") if env_name else ""
    hostname = str(config.get("hostname", "")).strip().rstrip(".")
    if require_targets and not target:
        raise ConfigurationError(
            f"{env_name or 'target_env_var'} deve estar definido para {hostname}"
        )
    return {
        "name": hostname,
        "type": str(config.get("record_type", "CNAME")).upper(),
        "content": target,
        "proxied": bool(config.get("proxied", True)),
        "ttl": int(config.get("ttl", 1)),
        "comment": (
            f"All-in-One MCP {config.get('environment', 'production')} "
            "gerenciado declarativamente"
        ),
    }


class CloudflareClient:
    def __init__(self, token: str) -> None:
        if not token:
            raise ConfigurationError("CLOUDFLARE_API_TOKEN não está definido")
        self._token = token

    def request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not path.startswith("/"):
            raise ConfigurationError(f"caminho de API inválido: {path}")
        body = (
            json.dumps(payload, separators=(",", ":")).encode("utf-8")
            if payload is not None
            else None
        )
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }
        if body is not None:
            headers["Content-Type"] = "application/json"

        connection = http.client.HTTPSConnection(API_HOST, timeout=30)
        try:
            connection.request(
                method,
                f"{API_PREFIX}{path}",
                body=body,
                headers=headers,
            )
            response = connection.getresponse()
            raw = response.read().decode("utf-8")
        finally:
            connection.close()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CloudflareAPIError(
                f"Cloudflare respondeu JSON inválido em {method} {path}"
            ) from exc
        if response.status >= 400 or data.get("success") is not True:
            messages = ", ".join(
                str(error.get("message", error))
                for error in data.get("errors", [])
            )
            raise CloudflareAPIError(
                f"Cloudflare rejeitou {method} {path}: "
                f"HTTP {response.status} {messages}".strip()
            )
        return data

    def zone_id(self, zone_name: str, account_id: str | None) -> str:
        explicit = os.getenv("CLOUDFLARE_ZONE_ID", "").strip()
        if explicit:
            return explicit
        query: dict[str, str] = {"name": zone_name, "status": "active"}
        if account_id:
            query["account.id"] = account_id
        data = self.request("GET", f"/zones?{urllib.parse.urlencode(query)}")
        results = data.get("result", [])
        if not isinstance(results, list) or len(results) != 1:
            raise CloudflareAPIError(
                f"zona {zone_name} não foi resolvida de forma única"
            )
        zone_id = str(results[0].get("id", "")).strip()
        if not zone_id:
            raise CloudflareAPIError(f"zona {zone_name} sem id")
        return zone_id

    def find_record(
        self,
        zone_id: str,
        name: str,
    ) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode(
            {
                "name": name,
                "per_page": "100",
            }
        )
        data = self.request(
            "GET",
            f"/zones/{zone_id}/dns_records?{query}",
        )
        result = data.get("result", [])
        if not isinstance(result, list):
            raise CloudflareAPIError(f"lista DNS inválida para {name}")
        return [item for item in result if isinstance(item, dict)]

    def upsert_record(
        self,
        zone_id: str,
        desired: Mapping[str, Any],
        *,
        apply: bool,
    ) -> str:
        name = str(desired["name"])
        existing = self.find_record(zone_id, name)
        if len(existing) > 1:
            raise CloudflareAPIError(
                f"mais de um registro existente para {name}; "
                "revisão manual necessária"
            )
        body = {
            "type": desired["type"],
            "name": name,
            "content": desired["content"],
            "proxied": desired["proxied"],
            "ttl": desired["ttl"],
            "comment": desired["comment"],
        }
        if not existing:
            if not apply:
                return "missing"
            self.request(
                "POST",
                f"/zones/{zone_id}/dns_records",
                body,
            )
            return "created"

        current = existing[0]
        if str(current.get("type", "")).upper() != str(desired["type"]).upper():
            raise CloudflareAPIError(
                f"conflito de tipo em {name}: "
                f"{current.get('type')} != {desired['type']}"
            )
        matches = (
            str(current.get("content", "")).rstrip(".").casefold()
            == str(desired["content"]).rstrip(".").casefold()
            and bool(current.get("proxied")) == bool(desired["proxied"])
            and int(current.get("ttl", 1)) == int(desired["ttl"])
        )
        if matches:
            return "unchanged"
        if not apply:
            return "drift"
        record_id = str(current.get("id", "")).strip()
        if not record_id:
            raise CloudflareAPIError(f"registro existente sem id: {name}")
        self.request(
            "PATCH",
            f"/zones/{zone_id}/dns_records/{record_id}",
            body,
        )
        return "updated"


def workspace_account_id() -> str | None:
    profile = load_json(WORKSPACE_PROFILE_PATH)
    account = profile.get("account")
    if not isinstance(account, Mapping):
        return None
    value = str(account.get("account_id", "")).strip()
    return value or None


def verify_https(health_url: str) -> None:
    request = urllib.request.Request(
        health_url,
        headers={"User-Agent": "aio-mcp-dns-validator/1.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(
                f"health check retornou HTTP {response.status}: {health_url}"
            )
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("status") != "ok":
        raise RuntimeError(f"health check não retornou status=ok: {health_url}")


def print_plan(records: Iterable[Mapping[str, Any]]) -> None:
    for record in records:
        print(
            f"{record['type']} {record['name']} -> {record['content']} "
            f"proxied={str(record['proxied']).lower()} ttl={record['ttl']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Valida ou aplica exclusivamente os DNS MCP sob "
            "brasildesconto.com.br, sem alterar o domínio raiz."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="Compara o estado remoto sem modificar registros (padrão).",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Cria ou atualiza somente os registros declarados.",
    )
    parser.add_argument(
        "--environment",
        choices=("production", "staging", "preview"),
        default="production",
    )
    parser.add_argument(
        "--confirm-zone",
        default="",
        help="Obrigatório no modo apply; deve ser brasildesconto.com.br.",
    )
    parser.add_argument(
        "--verify-https",
        action="store_true",
        help="Valida o /health HTTPS após conferir os registros.",
    )
    args = parser.parse_args()

    plan = load_plan()
    records = list(
        iter_plan_records(
            plan,
            environment=args.environment,
            require_targets=True,
        )
    )
    validate_plan(plan)
    print_plan(records)

    apply = bool(args.apply)
    if apply and args.confirm_zone.casefold() != ALLOWED_ZONE:
        raise ConfigurationError(
            "--confirm-zone brasildesconto.com.br é obrigatório para aplicar"
        )

    token = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
    client = CloudflareClient(token)
    zone_id = client.zone_id(ALLOWED_ZONE, workspace_account_id())

    errors: list[str] = []
    for record in records:
        state = client.upsert_record(zone_id, record, apply=apply)
        print(f"{state.upper()}: {record['name']}")
        if not apply and state in {"missing", "drift"}:
            errors.append(f"{record['name']}={state}")

    if args.verify_https:
        canonical = cast_mapping(plan["canonical"], "canonical")
        if args.environment != "production":
            selected = next(
                item
                for item in plan["environments"]
                if item["environment"] == args.environment
            )
            hostname = selected["hostname"]
            health_url = f"https://{hostname}/health"
        else:
            health_url = str(canonical["health_url"])
        verify_https(health_url)
        print(f"OK: TLS e health confirmados em {health_url}")

    if errors:
        print("DNS MCP divergente: " + ", ".join(errors), file=sys.stderr)
        return 1
    print("DNS MCP aplicado." if apply else "DNS MCP validado.")
    return 0


def redacted(message: str) -> str:
    token = os.getenv("CLOUDFLARE_API_TOKEN", "")
    return message.replace(token, "***REDACTED***") if token else message


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Erro DNS MCP: {redacted(str(exc))}", file=sys.stderr)
        raise SystemExit(1)
