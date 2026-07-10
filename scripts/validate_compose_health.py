#!/usr/bin/env python3
"""Valida o Docker Compose local e os healthchecks HTTP principais."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMPOSE_FILE = Path("infra/docker/docker-compose.yml")


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


def run_checked(args: list[str]) -> None:
    try:
        subprocess.run(args, cwd=ROOT, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Comando nao encontrado: {args[0]}") from exc
    except subprocess.CalledProcessError as exc:
        joined = " ".join(args)
        raise RuntimeError(f"{joined} falhou com codigo {exc.returncode}") from exc


def is_healthy(probe: ServiceProbe, timeout_seconds: float) -> bool:
    try:
        with urllib.request.urlopen(probe.url, timeout=timeout_seconds) as response:
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compose-file", default=str(DEFAULT_COMPOSE_FILE))
    parser.add_argument("--timeout-seconds", type=int, default=240)
    parser.add_argument("--probe-timeout-seconds", type=float, default=3.0)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--down-after", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    compose_file = Path(args.compose_file)
    if not compose_file.is_absolute():
        compose_file = ROOT / compose_file
    if not compose_file.is_file():
        print(f"Arquivo compose nao encontrado: {compose_file}", file=sys.stderr)
        return 2

    compose = ["docker", "compose", "-f", str(compose_file)]
    up_args = [*compose, "up", "-d"]
    if not args.skip_build:
        up_args.append("--build")

    try:
        run_checked([*compose, "config", "--quiet"])
        run_checked(up_args)
        pending = wait_for_health(args.timeout_seconds, args.probe_timeout_seconds)
        if pending:
            subprocess.run([*compose, "ps"], cwd=ROOT, check=False)
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
