from __future__ import annotations

import argparse
import http.client
import json
import os
import socket
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "cloudflare" / "workspace_profile.json"
DEFAULT_TUNNEL_TOKEN_ENV = "CLOUDFLARE_TUNNEL_TOKEN"
CLOUDFLARE_API_HOST = "api.cloudflare.com"


def run(args: list[str], timeout: int = 45) -> tuple[int, str]:
    environment = os.environ.copy()
    environment.setdefault("CI", "1")
    environment.setdefault("WRANGLER_SEND_METRICS", "false")
    environment.setdefault("NO_UPDATE_NOTIFIER", "1")
    try:
        process = subprocess.run(
            args,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
            env=environment,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        return 124, f"timeout apos {timeout}s: {' '.join(args)}\n{output}"
    return process.returncode, process.stdout


def get_cloudflare_bearer_token(errors: list[str]) -> str:
    env_token = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
    if env_token:
        return env_token

    returncode, output = run(["wrangler", "auth", "token", "--json"], timeout=90)
    if returncode:
        fail("nao foi possivel obter token OAuth local do wrangler.", errors)
        return ""
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        fail("wrangler auth token --json retornou JSON invalido.", errors)
        return ""
    token = str(data.get("token") or data.get("accessToken") or data.get("value") or "").strip()
    if not token:
        fail("wrangler auth token --json nao retornou bearer token utilizavel.", errors)
    return token


def cloudflare_https_get(path: str, errors: list[str], headers: dict[str, str] | None = None) -> dict:
    if not path.startswith("/client/v4/"):
        fail(f"Caminho Cloudflare fora da API permitida: {path}", errors)
        return {}
    connection = http.client.HTTPSConnection(CLOUDFLARE_API_HOST, timeout=30)
    try:
        connection.request("GET", path, headers=headers or {})
        response = connection.getresponse()
        return json.loads(response.read().decode("utf-8"))
    except json.JSONDecodeError:
        fail(f"API Cloudflare respondeu JSON invalido para {path}.", errors)
    except Exception as exc:
        fail(f"API Cloudflare indisponivel para {path}: {exc}", errors)
    finally:
        connection.close()
    return {}


def cloudflare_api_get(profile: dict, path: str, errors: list[str]) -> dict:
    token = get_cloudflare_bearer_token(errors)
    if not token:
        return {}
    return cloudflare_https_get(
        f"/client/v4{path}",
        errors,
        {"Authorization": f"Bearer {token}"},
    )


def ok(message: str) -> None:
    print(f"OK: {message}")


def warn(message: str) -> None:
    print(f"AVISO: {message}")


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)
    print(f"ERRO: {message}")


def load_profile(errors: list[str]) -> dict:
    if not PROFILE.is_file():
        fail("Perfil Cloudflare ausente: config/cloudflare/workspace_profile.json", errors)
        return {}
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    serialized = json.dumps(profile, sort_keys=True)
    forbidden = ["BEGIN ", "AQ.", "-----"]
    for marker in forbidden:
        if marker in serialized:
            fail(f"Perfil Cloudflare contem material sensivel ou token: {marker}", errors)
    return profile


def validate_cloudflared(profile: dict, errors: list[str]) -> None:
    returncode, output = run(["cloudflared", "--version"])
    if returncode:
        fail("cloudflared nao esta instalado ou nao responde.", errors)
        return
    expected = profile.get("tunnel", {}).get("installed_version_verified")
    if expected and expected not in output:
        warn(f"cloudflared instalado, mas versao difere da registrada: {output.strip()}")
    else:
        ok(output.strip())


def validate_wrangler(profile: dict, errors: list[str]) -> None:
    returncode, version = run(["wrangler", "--version"])
    if returncode:
        fail("wrangler nao esta instalado.", errors)
        return
    ok(version.strip())
    returncode, whoami = run(["wrangler", "whoami"], timeout=90)
    if returncode:
        fail("wrangler nao esta autenticado por OAuth ou CLOUDFLARE_API_TOKEN.", errors)
        return
    account_id = profile.get("account", {}).get("account_id", "")
    if account_id and account_id not in whoami:
        fail("wrangler autenticado em conta diferente da conta Cloudflare versionada.", errors)
    else:
        ok("wrangler autenticado na conta Cloudflare esperada")


def validate_pages_project(profile: dict, errors: list[str]) -> None:
    pages = profile.get("pages", {})
    returncode, output = run(["wrangler", "pages", "project", "list"], timeout=90)
    if returncode:
        fail("nao foi possivel listar Cloudflare Pages via wrangler.", errors)
        return
    project = pages.get("project_name", "")
    missing = [item for item in [project, *pages.get("known_domains", [])] if item and item not in output]
    if missing:
        fail(f"Cloudflare Pages nao confirmou os itens esperados: {', '.join(missing)}", errors)
    else:
        ok(f"Cloudflare Pages confirmou {project}")


def validate_tunnel_remote_state(profile: dict, errors: list[str]) -> bool:
    account_id = profile.get("account", {}).get("account_id", "")
    tunnel = profile.get("tunnel", {})
    tunnel_id = tunnel.get("tunnel_id", "")
    tunnel_name = tunnel.get("tunnel_name", "")
    if not account_id or not tunnel_id:
        warn("perfil Cloudflare nao registra tunnel_id; validacao remota do tunnel ignorada")
        return False

    detail = cloudflare_api_get(profile, f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}", errors)
    if not detail:
        return False
    if detail.get("success") is not True:
        messages = ", ".join(error.get("message", "") for error in detail.get("errors", []))
        fail(f"Cloudflare Tunnel nao confirmou o tunnel versionado: {messages}", errors)
        return False
    result = detail.get("result") or {}
    if result.get("name") != tunnel_name:
        fail("Cloudflare Tunnel remoto tem nome diferente do perfil versionado.", errors)
        return False
    if result.get("status") != "healthy":
        fail(f"Cloudflare Tunnel {tunnel_name} nao esta healthy: {result.get('status')}", errors)
        return False

    config = cloudflare_api_get(
        profile,
        f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations",
        errors,
    )
    if not config:
        return False
    if config.get("success") is not True:
        messages = ", ".join(error.get("message", "") for error in config.get("errors", []))
        fail(f"Configuracao remota do Cloudflare Tunnel nao foi confirmada: {messages}", errors)
        return False
    ingress = (config.get("result") or {}).get("config", {}).get("ingress", [])
    for hostname in tunnel.get("desired_public_hostnames", []):
        expected_host = hostname.get("hostname")
        expected_origin = hostname.get("origin")
        if not expected_host:
            continue
        match = next((rule for rule in ingress if rule.get("hostname") == expected_host), None)
        if not match:
            fail(f"Cloudflare Tunnel nao contem ingress para {expected_host}.", errors)
            return False
        if expected_origin and match.get("service") != expected_origin:
            fail(
                f"Cloudflare Tunnel {expected_host} aponta para {match.get('service')}, esperado {expected_origin}.",
                errors,
            )
            return False
    ok(f"Cloudflare Tunnel {tunnel_name} healthy com ingress versionado")
    return True


def validate_codex_mcp(profile: dict, errors: list[str]) -> None:
    returncode, output = run(["codex", "mcp", "list"], timeout=60)
    if returncode:
        fail("nao foi possivel listar MCPs do Codex.", errors)
        return
    expected = [
        profile["mcp"]["docs"]["name"],
        profile["mcp"]["docs"]["url"],
        profile["mcp"]["api"]["name"],
        profile["mcp"]["api"]["url"],
        profile["mcp"]["api"]["bearer_token_env_var"],
    ]
    missing = [item for item in expected if item not in output]
    if missing:
        fail(f"MCP Cloudflare incompleto: {', '.join(missing)}", errors)
    else:
        ok("MCPs Cloudflare cadastrados no Codex")


def validate_network(errors: list[str]) -> None:
    try:
        with socket.create_connection(("region1.v2.argotunnel.com", 7844), timeout=10):
            ok("porta Cloudflare Tunnel 7844 acessivel")
    except OSError as exc:
        fail(f"porta Cloudflare Tunnel 7844 indisponivel: {exc}", errors)
    data = cloudflare_https_get("/client/v4/ips", errors)
    if data.get("success") is True:
        ok("API Cloudflare acessivel")
    elif data:
        fail("API Cloudflare respondeu sem success=true.", errors)


def validate_tunnel_activation(profile: dict, errors: list[str], strict: bool) -> None:
    if validate_tunnel_remote_state(profile, errors):
        return

    token_env = profile["tunnel"].get("token_env_var", DEFAULT_TUNNEL_TOKEN_ENV)
    service_name = profile["tunnel"]["systemd_service"]
    token_present = bool(os.getenv(token_env, "").strip())
    returncode, output = run(["systemctl", "is-active", service_name], timeout=15)
    service_active = returncode == 0 and output.strip() == "active"
    if service_active:
        ok(f"servico {service_name} ativo")
        return
    message = (
        f"servico {service_name} ainda nao esta ativo; defina {token_env} e execute "
        "sudo -E python3 scripts/configure_cloudflare_wsl.py --apply --install-service"
    )
    if strict or token_present:
        fail(message, errors)
    else:
        warn(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida a configuracao Cloudflare WSL do workspace.")
    parser.add_argument("--strict", action="store_true", help="Exige tunnel token e servico systemd ativo.")
    args = parser.parse_args()
    errors: list[str] = []
    profile = load_profile(errors)
    if profile:
        validate_cloudflared(profile, errors)
        validate_wrangler(profile, errors)
        validate_pages_project(profile, errors)
        validate_codex_mcp(profile, errors)
        validate_network(errors)
        validate_tunnel_activation(profile, errors, args.strict)
    if errors:
        print(f"Cloudflare WSL invalido: {len(errors)} erro(s).")
        return 1
    print("Cloudflare WSL validado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
