#!/usr/bin/env python3
"""Configura e valida DNS persistente do WSL para o workspace All-in-One."""

from __future__ import annotations

import argparse
import configparser
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "autonomy" / "wsl_dns_policy.json"
WSL_CONF = Path("/etc/wsl.conf")


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def run(args: list[str], timeout: int = 30) -> tuple[int, str]:
    process = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=timeout,
    )
    return process.returncode, process.stdout


def is_wsl() -> bool:
    try:
        return "microsoft" in Path("/proc/version").read_text(encoding="utf-8").lower()
    except OSError:
        return False


def render_resolved_dropin(policy: dict) -> str:
    resolved = policy["resolved"]
    return "\n".join(
        [
            "[Resolve]",
            f"DNS={' '.join(resolved['dns'])}",
            f"FallbackDNS={' '.join(resolved['fallback_dns'])}",
            f"Domains={' '.join(resolved['domains'])}",
            f"DNSStubListener={resolved['dns_stub_listener']}",
            "",
        ]
    )


def read_wsl_conf() -> configparser.ConfigParser:
    parser = configparser.ConfigParser()
    parser.optionxform = str
    if WSL_CONF.exists():
        parser.read(WSL_CONF, encoding="utf-8")
    return parser


def render_wsl_conf(policy: dict, parser: configparser.ConfigParser) -> str:
    if "boot" not in parser:
        parser["boot"] = {}
    if "network" not in parser:
        parser["network"] = {}
    parser["boot"]["systemd"] = "true"
    parser["network"]["generateResolvConf"] = "false"
    parser["network"]["hostname"] = policy["wsl"]["hostname"]

    lines: list[str] = []
    for section in parser.sections():
        lines.append(f"[{section}]")
        for key, value in parser[section].items():
            lines.append(f"{key}={value}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_if_changed(path: Path, content: str) -> bool:
    previous = path.read_text(encoding="utf-8") if path.exists() and path.is_file() else None
    if previous == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def require_root() -> None:
    if os.geteuid() != 0:
        raise RuntimeError(
            "Aplicacao de DNS WSL exige root. Use: "
            "wsl.exe -d Ubuntu -u root -- bash -lc "
            f"'cd {ROOT} && python3 scripts/configure_wsl_dns.py --apply'"
        )


def apply_policy(policy: dict) -> list[str]:
    require_root()
    changed: list[str] = []

    desired_wsl_conf = render_wsl_conf(policy, read_wsl_conf())
    if write_if_changed(WSL_CONF, desired_wsl_conf):
        changed.append(str(WSL_CONF))

    dropin = Path(policy["resolved"]["dropin_path"])
    if write_if_changed(dropin, render_resolved_dropin(policy)):
        changed.append(str(dropin))

    resolv_conf = Path(policy["resolved"]["resolv_conf"])
    target = Path(policy["resolved"]["resolv_conf_symlink_target"])
    if not resolv_conf.is_symlink() or os.readlink(resolv_conf) != str(target):
        if resolv_conf.exists() or resolv_conf.is_symlink():
            resolv_conf.unlink()
        resolv_conf.symlink_to(target)
        changed.append(str(resolv_conf))

    returncode, _ = run(["systemctl", "is-active", "systemd-resolved"], timeout=15)
    if returncode == 0:
        run(["systemctl", "restart", "systemd-resolved"], timeout=30)
    else:
        run(["systemctl", "enable", "--now", "systemd-resolved"], timeout=30)
    return changed


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_wsl_conf(policy: dict, errors: list[str]) -> None:
    parser = read_wsl_conf()
    expect(
        parser.get("boot", "systemd", fallback="").lower() == "true",
        "/etc/wsl.conf deve declarar [boot] systemd=true.",
        errors,
    )
    expect(
        parser.get("network", "generateResolvConf", fallback="").lower() == "false",
        "/etc/wsl.conf deve declarar [network] generateResolvConf=false.",
        errors,
    )
    expect(
        parser.get("network", "hostname", fallback="") == policy["wsl"]["hostname"],
        f"/etc/wsl.conf deve declarar hostname={policy['wsl']['hostname']}.",
        errors,
    )


def validate_resolved(policy: dict, errors: list[str]) -> None:
    resolved = policy["resolved"]
    dropin = Path(resolved["dropin_path"])
    expect(dropin.is_file(), f"Drop-in DNS ausente: {dropin}", errors)
    if dropin.is_file():
        expect(
            dropin.read_text(encoding="utf-8") == render_resolved_dropin(policy),
            f"Drop-in DNS diverge da politica: {dropin}",
            errors,
        )

    resolv_conf = Path(resolved["resolv_conf"])
    expect(resolv_conf.is_symlink(), "/etc/resolv.conf deve ser symlink.", errors)
    if resolv_conf.is_symlink():
        expect(
            os.readlink(resolv_conf) == resolved["resolv_conf_symlink_target"],
            "/etc/resolv.conf deve apontar para o stub do systemd-resolved.",
            errors,
        )
    if resolv_conf.exists():
        content = resolv_conf.read_text(encoding="utf-8", errors="ignore")
        expect(
            f"nameserver {resolved['stub_nameserver']}" in content,
            "resolv.conf deve expor nameserver 127.0.0.53.",
            errors,
        )

    returncode, output = run(["systemctl", "is-active", "systemd-resolved"], timeout=15)
    expect(
        returncode == 0 and output.strip() == "active",
        "systemd-resolved deve estar ativo.",
        errors,
    )


def validate_tailscale(policy: dict, errors: list[str]) -> None:
    if not policy.get("tailscale", {}).get("preserve_magic_dns", False):
        return
    returncode, output = run(["tailscale", "status", "--json"], timeout=60)
    if returncode:
        return
    try:
        status = json.loads(output)
    except json.JSONDecodeError:
        errors.append("tailscale status --json retornou JSON invalido.")
        return
    if status.get("BackendState") != "Running":
        return
    returncode, resolvectl = run(["resolvectl", "status"], timeout=30)
    if returncode:
        errors.append("resolvectl status falhou com Tailscale ativo.")
        return
    expected_dns = policy["tailscale"]["expected_dns_server"]
    expected_suffix = policy["tailscale"]["expected_search_suffix"]
    expect(expected_dns in resolvectl, f"MagicDNS deve preservar {expected_dns}.", errors)
    expect(expected_suffix in resolvectl, f"MagicDNS deve preservar {expected_suffix}.", errors)


def validate_hosts(policy: dict, errors: list[str]) -> None:
    for host in policy["validation"]["hosts"]:
        try:
            socket.getaddrinfo(host, 443)
        except socket.gaierror as exc:
            errors.append(f"DNS nao resolveu {host}: {exc}")


def validate(policy: dict) -> list[str]:
    errors: list[str] = []
    expect(is_wsl(), "Este validador deve rodar dentro do WSL.", errors)
    validate_wsl_conf(policy, errors)
    validate_resolved(policy, errors)
    validate_tailscale(policy, errors)
    validate_hosts(policy, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Aplica a politica em /etc.")
    parser.add_argument("--check", action="store_true", help="Valida o estado atual.")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    policy = load_policy()
    if args.apply:
        changed = apply_policy(policy)
        print(
            "DNS WSL aplicado."
            + (f" Arquivos alterados: {', '.join(changed)}" if changed else " Sem alteracoes.")
        )

    errors = validate(policy)
    if errors:
        print("DNS WSL invalido:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DNS WSL validado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
