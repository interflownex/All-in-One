#!/usr/bin/env python3
"""Valida o Docker Compose local e os healthchecks HTTP principais."""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMPOSE_FILE = Path("infra/docker/docker-compose.yml")
REQUIRED_HOST_PORTS = (
    5432,
    5672,
    6379,
    8100,
    8101,
    8102,
    8103,
    8104,
    8105,
    8106,
    8107,
    8108,
    8109,
    8110,
    8111,
    8112,
    8113,
    8114,
    8115,
    15672,
    27017,
)


@dataclass(frozen=True)
class ServiceProbe:
    name: str
    port: int

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}/health"


SERVICE_PROBES: tuple[ServiceProbe, ...] = (
    ServiceProbe("api-hub", 8100),
    ServiceProbe("identity", 8101),
    ServiceProbe("finance", 8102),
    ServiceProbe("marketplace", 8103),
    ServiceProbe("delivery", 8104),
    ServiceProbe("services", 8105),
    ServiceProbe("mobility", 8106),
    ServiceProbe("erp", 8107),
    ServiceProbe("wms", 8108),
    ServiceProbe("tms", 8109),
    ServiceProbe("crm", 8110),
    ServiceProbe("health", 8111),
    ServiceProbe("jobs", 8112),
)


def run_checked(args: list[str], timeout_seconds: int) -> None:
    try:
        subprocess.run(args, cwd=ROOT, check=True, timeout=timeout_seconds)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Comando nao encontrado: {args[0]}") from exc
    except subprocess.CalledProcessError as exc:
        joined = " ".join(args)
        raise RuntimeError(f"{joined} falhou com codigo {exc.returncode}") from exc
    except subprocess.TimeoutExpired as exc:
        joined = " ".join(args)
        raise RuntimeError(f"{joined} excedeu {timeout_seconds} segundo(s)") from exc


def is_healthy(probe: ServiceProbe, timeout_seconds: float) -> bool:
    try:
        # B310: URLs sao montadas exclusivamente a partir de portas localhost
        # declaradas em SERVICE_PROBES; nao ha entrada externa do usuario aqui.
        with urllib.request.urlopen(probe.url, timeout=timeout_seconds) as response:  # nosec B310
            body = response.read().decode("utf-8", errors="replace")
            if not 200 <= response.status < 300:
                return False
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                return '"ok"' in body or "ok" in body.lower()
            return payload.get("status") == "ok"
    except (TimeoutError, urllib.error.URLError, OSError):
        return False


def wait_for_health(timeout_seconds: int, probe_timeout_seconds: float) -> set[str]:
    pending = {probe.name for probe in SERVICE_PROBES}
    probes_by_name = {probe.name: probe for probe in SERVICE_PROBES}
    deadline = time.monotonic() + timeout_seconds

    while pending and time.monotonic() < deadline:
        for service_name in tuple(sorted(pending)):
            probe = probes_by_name[service_name]
            if is_healthy(probe, timeout_seconds=probe_timeout_seconds):
                print(f"{probe.name} healthy em {probe.url}", flush=True)
                pending.remove(service_name)
        if pending:
            time.sleep(1)

    return pending


def bound_ports(ports: tuple[int, ...] = REQUIRED_HOST_PORTS) -> list[int]:
    occupied: list[int] = []
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                occupied.append(port)
    return occupied


def print_compose_diagnostics(compose: list[str], pending: set[str]) -> None:
    subprocess.run([*compose, "ps"], cwd=ROOT, check=False)
    if pending:
        subprocess.run([*compose, "logs", "--tail", "80", *sorted(pending)], cwd=ROOT, check=False)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compose-file", default=str(DEFAULT_COMPOSE_FILE))
    parser.add_argument("--env-file", default=None)
    parser.add_argument("--project-name", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=240)
    parser.add_argument("--probe-timeout-seconds", type=float, default=3.0)
    parser.add_argument("--command-timeout-seconds", type=int, default=300)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--down-after", action="store_true")
    parser.add_argument("--require-free-ports", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    compose_file = Path(args.compose_file)
    if not compose_file.is_absolute():
        compose_file = ROOT / compose_file
    if not compose_file.is_file():
        print(f"Arquivo compose nao encontrado: {compose_file}", file=sys.stderr)
        return 2

    compose = ["docker", "compose"]
    if args.env_file:
        env_file = Path(args.env_file)
        if not env_file.is_absolute():
            env_file = ROOT / env_file
        if not env_file.is_file():
            print(f"Arquivo env do compose nao encontrado: {env_file}", file=sys.stderr)
            return 2
        compose.extend(["--env-file", str(env_file)])
    if args.project_name:
        compose.extend(["--project-name", args.project_name])
    compose.extend(["-f", str(compose_file)])
    up_args = [*compose, "up", "-d"]
    if args.skip_build:
        up_args.append("--no-build")
    else:
        up_args.append("--build")

    try:
        if args.require_free_ports:
            occupied = bound_ports()
            if occupied:
                print(
                    "Portas publicadas pelo Compose ja estao em uso antes do gate: "
                    f"{', '.join(str(port) for port in occupied)}",
                    file=sys.stderr,
                )
                return 1
        run_checked([*compose, "config", "--quiet"], timeout_seconds=args.command_timeout_seconds)
        run_checked(up_args, timeout_seconds=args.command_timeout_seconds)
        pending = wait_for_health(args.timeout_seconds, args.probe_timeout_seconds)
        if pending:
            print_compose_diagnostics(compose, pending)
            print(
                "Servicos sem health HTTP dentro de "
                f"{args.timeout_seconds} segundo(s): {', '.join(sorted(pending))}",
                file=sys.stderr,
            )
            return 1
        print(f"Docker Compose validado: {len(SERVICE_PROBES)} APIs FastAPI healthy.")
        return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        if args.down_after:
            subprocess.run([*compose, "down", "--remove-orphans", "-v"], cwd=ROOT, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
