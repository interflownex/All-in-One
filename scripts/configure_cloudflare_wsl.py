from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "cloudflare" / "workspace_profile.json"
DEFAULT_SYSTEMD_SERVICE = "cloudflared-all-in-one.service"


def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def load_profile() -> dict:
    return json.loads(PROFILE.read_text(encoding="utf-8"))


def redacted(text: str) -> str:
    token = os.getenv("CLOUDFLARE_TUNNEL_TOKEN", "")
    api_token = os.getenv("CLOUDFLARE_API_TOKEN", "")
    for secret in [token, api_token]:
        if secret:
            text = text.replace(secret, "***REDACTED***")
    return text


def ensure_command(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"Comando ausente no PATH: {name}")
    return path


def ensure_codex_cloudflare_mcp(profile: dict) -> None:
    docs = profile["mcp"]["docs"]
    api = profile["mcp"]["api"]
    commands = [
        ["codex", "mcp", "add", docs["name"], "--url", docs["url"]],
        [
            "codex",
            "mcp",
            "add",
            api["name"],
            "--url",
            api["url"],
            "--bearer-token-env-var",
            api["bearer_token_env_var"],
        ],
    ]
    for command in commands:
        result = run(command, check=False)
        output = redacted(result.stdout)
        if result.returncode and "already exists" not in output and "ja existe" not in output:
            raise RuntimeError(output.strip())


def validate_wrangler_auth() -> None:
    ensure_command("wrangler")
    result = run(["wrangler", "whoami"], check=False)
    if result.returncode:
        raise RuntimeError(
            "Wrangler nao esta autenticado. Execute `wrangler login` ou defina CLOUDFLARE_API_TOKEN fora do Git."
        )


def validate_cloudflared() -> None:
    ensure_command("cloudflared")
    result = run(["cloudflared", "--version"])
    if "cloudflared version" not in result.stdout:
        raise RuntimeError("Nao foi possivel validar a versao do cloudflared.")


def write_tunnel_env_file(profile: dict, token: str) -> Path:
    token_file = Path(profile["tunnel"]["token_env_file"])
    token_file.parent.mkdir(parents=True, exist_ok=True)
    previous_umask = os.umask(0o177)
    try:
        token_file.write_text(f'CLOUDFLARE_TUNNEL_TOKEN="{token}"\n', encoding="utf-8")
    finally:
        os.umask(previous_umask)
    token_file.chmod(0o600)
    return token_file


def install_systemd_service(profile: dict, token: str) -> None:
    if os.geteuid() != 0:
        raise RuntimeError(
            "Instalacao do servico exige root. Use: sudo -E python3 scripts/configure_cloudflare_wsl.py --apply --install-service"
        )
    service_name = profile["tunnel"].get("systemd_service", DEFAULT_SYSTEMD_SERVICE)
    token_file = write_tunnel_env_file(profile, token)
    service_path = Path("/etc/systemd/system") / service_name
    service = f"""[Unit]
Description=Cloudflare Tunnel - All-in-One WSL
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
EnvironmentFile={token_file}
ExecStart=/usr/bin/cloudflared tunnel --no-autoupdate run --token ${{CLOUDFLARE_TUNNEL_TOKEN}}
Restart=always
RestartSec=5s
User=root

[Install]
WantedBy=multi-user.target
"""
    service_path.write_text(service, encoding="utf-8")
    service_path.chmod(0o644)
    run(["systemctl", "daemon-reload"])
    run(["systemctl", "enable", service_name])
    run(["systemctl", "restart", service_name])


def print_summary(profile: dict, service_action: str) -> None:
    pages = profile["pages"]
    tunnel = profile["tunnel"]
    print("Cloudflare configurado para o workspace.")
    print(f"Pages: {pages['project_name']} -> {', '.join(pages['known_domains'])}")
    print(f"MCP: {profile['mcp']['docs']['name']} e {profile['mcp']['api']['name']}")
    print(f"Tunnel: {tunnel['tunnel_name']} via {tunnel['token_env_var']} ({service_action})")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Configura o perfil Cloudflare do All-in-One no WSL sem versionar segredos."
    )
    parser.add_argument("--apply", action="store_true", help="Aplica MCPs e valida CLI local.")
    parser.add_argument(
        "--install-service",
        action="store_true",
        help="Instala ou atualiza o servico systemd quando CLOUDFLARE_TUNNEL_TOKEN estiver definido.",
    )
    args = parser.parse_args()

    profile = load_profile()
    validate_cloudflared()
    validate_wrangler_auth()
    service_action = "nao instalado; token ausente"

    if args.apply:
        ensure_codex_cloudflare_mcp(profile)

    token = os.getenv(profile["tunnel"]["token_env_var"], "").strip()
    if args.install_service:
        if not token:
            raise RuntimeError(
                f"{profile['tunnel']['token_env_var']} nao esta definido no ambiente; nao ha segredo para instalar o tunnel."
            )
        install_systemd_service(profile, token)
        service_action = "servico instalado e reiniciado"

    print_summary(profile, service_action)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Erro Cloudflare: {redacted(str(exc))}", file=sys.stderr)
        raise SystemExit(1)
