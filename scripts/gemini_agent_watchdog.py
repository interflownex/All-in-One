#!/usr/bin/env python3
"""Watchdog periodico do Gemini para evitar travamentos silenciosos."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INTERVAL_MINUTES = 30
STOP = False


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def run_cmd(args: list[str], timeout: int = 10) -> tuple[int, str]:
    try:
        result = subprocess.run(
            args,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, (result.stdout or result.stderr or "").strip()
    except (subprocess.TimeoutExpired, OSError) as exc:
        return 99, str(exc)


def process_count(pattern: str) -> int:
    rc, out = run_cmd(["pgrep", "-f", pattern], timeout=5)
    if rc != 0 or not out:
        return 0
    return len([line for line in out.splitlines() if line.strip()])


def meminfo() -> dict[str, int] | None:
    path = Path("/proc/meminfo")
    if not path.is_file():
        return None
    values: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, _, tail = line.partition(":")
        parts = tail.strip().split()
        if not key or not parts:
            continue
        try:
            values[key.strip()] = int(parts[0])
        except ValueError:
            continue
    return {
        "total_kb": values.get("MemTotal", -1),
        "available_kb": values.get("MemAvailable", -1),
        "swap_free_kb": values.get("SwapFree", -1),
    }


def lock_status(scope: str) -> dict:
    rc, out = run_cmd(
        [
            sys.executable,
            "scripts/multi_agent_sync_guard.py",
            "status",
            "--scope",
            scope,
        ],
        timeout=10,
    )
    if rc != 0:
        return {"ok": False, "error": out}
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        return {"ok": False, "error": "saida invalida", "raw": out}
    payload["ok"] = True
    return payload


def git_status() -> dict[str, str | int]:
    rc1, branch = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"], timeout=8)
    rc2, status = run_cmd(
        ["git", "status", "--porcelain=v1", "--branch", "-uno"], timeout=8
    )
    if rc1 != 0:
        return {"ok": 0, "error": (branch or status)}
    if rc2 != 0:
        return {
            "ok": 1,
            "branch": branch.splitlines()[0] if branch else "",
            "status_preview": "status_git_indisponivel",
            "warning": status,
        }
    return {
        "ok": 1,
        "branch": branch.splitlines()[0] if branch else "",
        "status_preview": " | ".join(status.splitlines()[:5]),
    }


def loadavg() -> dict[str, float] | None:
    try:
        a, b, c = os.getloadavg()
    except OSError:
        return None
    return {"1m": round(a, 3), "5m": round(b, 3), "15m": round(c, 3)}


def disk() -> dict[str, int]:
    d = shutil.disk_usage(ROOT)
    used_percent = int((d.used / d.total) * 100) if d.total else -1
    return {
        "total_bytes": d.total,
        "used_bytes": d.used,
        "free_bytes": d.free,
        "used_percent": used_percent,
    }


def snapshot(scope: str) -> dict:
    return {
        "timestamp": now_iso(),
        "scope": scope,
        "host": os.uname().nodename,
        "python": sys.version.split()[0],
        "vscode_processes": process_count("code|code-server"),
        "gemini_processes": process_count("gemini|Gemini"),
        "node_processes": process_count("node"),
        "loadavg": loadavg(),
        "memory": meminfo(),
        "disk": disk(),
        "git": git_status(),
        "lock": lock_status(scope),
    }


def classify(data: dict) -> tuple[str, list[str]]:
    status = "ok"
    alerts: list[str] = []

    used_percent = int((data.get("disk") or {}).get("used_percent", 0))
    if used_percent >= 95:
        status = "critico"
        alerts.append("disco_acima_95")
    elif used_percent >= 90:
        status = "atencao"
        alerts.append("disco_acima_90")

    available_kb = int((data.get("memory") or {}).get("available_kb", -1))
    if available_kb != -1 and available_kb < 512000:
        status = "critico"
        alerts.append("memoria_disponivel_baixa")
    elif available_kb != -1 and available_kb < 1024000 and status == "ok":
        status = "atencao"
        alerts.append("memoria_disponivel_atencao")

    if int((data.get("git") or {}).get("ok", 0)) == 0:
        status = "critico"
        alerts.append("git_inacessivel")

    if not (data.get("lock") or {}).get("ok", True) and status == "ok":
        status = "atencao"
        alerts.append("status_lock_falhou")

    return status, alerts


def print_line(status: str, data: dict, alerts: list[str]) -> None:
    branch = (data.get("git") or {}).get("branch") or "?"
    used_percent = (data.get("disk") or {}).get("used_percent")
    available_kb = (data.get("memory") or {}).get("available_kb")
    mem_mb = int(available_kb) // 1024 if isinstance(available_kb, int) else -1
    summary = ",".join(alerts) if alerts else "sem_alertas"
    print(
        f"[{data['timestamp']}] watchdog={status} branch={branch} "
        f"disk={used_percent}% mem_avail_mb={mem_mb} alerts={summary}",
        flush=True,
    )


def on_signal(sig: int, _frame: object) -> None:
    global STOP
    STOP = True
    print(f"Encerrando watchdog por sinal {sig}.", flush=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scope", default="workspace")
    p.add_argument("--interval-minutes", type=int, default=DEFAULT_INTERVAL_MINUTES)
    p.add_argument("--cycles", type=int, default=0)
    p.add_argument(
        "--log-file",
        default="reports/monitoring/gemini_watchdog.jsonl",
        help="Arquivo JSONL de evidencias.",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.interval_minutes < 1:
        print("interval-minutes deve ser >= 1", file=sys.stderr)
        return 2

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    log_path = Path(args.log_file)
    if not log_path.is_absolute():
        log_path = ROOT / log_path
    interval = args.interval_minutes * 60

    print(
        f"Iniciando watchdog Gemini. intervalo={args.interval_minutes}m log={log_path}",
        flush=True,
    )

    cycle = 0
    while not STOP:
        data = snapshot(args.scope)
        status, alerts = classify(data)
        data["watchdog_status"] = status
        data["alerts"] = alerts

        # Recria o diretorio a cada ciclo para resistir a limpeza externa.
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(data, ensure_ascii=True) + "\n")

        print_line(status, data, alerts)

        cycle += 1
        if args.cycles > 0 and cycle >= args.cycles:
            break
        time.sleep(interval)

    print("Watchdog Gemini finalizado.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
