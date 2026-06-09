from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TTL_MINUTES = 120


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


def git_path(relative: str) -> Path:
    resolved = run_git("rev-parse", "--git-path", relative).stdout.strip()
    path = Path(resolved)
    return path if path.is_absolute() else ROOT / path


def lock_path() -> Path:
    return git_path("all-in-one-agent.lock")


def now_utc() -> datetime:
    return datetime.now(UTC)


def read_lock(path: Path | None = None) -> dict[str, Any] | None:
    target = path or lock_path()
    if not target.is_file():
        return None
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"invalid": True, "path": str(target)}
    payload["path"] = str(target)
    return payload


def lock_is_stale(payload: dict[str, Any], ttl_minutes: int) -> bool:
    try:
        acquired_at = datetime.fromisoformat(str(payload["acquired_at"]))
    except (KeyError, TypeError, ValueError):
        return True
    if acquired_at.tzinfo is None:
        acquired_at = acquired_at.replace(tzinfo=UTC)
    return now_utc() - acquired_at > timedelta(minutes=ttl_minutes)


def acquire_lock(agent: str, activity: str, ttl_minutes: int) -> dict[str, Any]:
    path = lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_lock(path)
    if existing and not lock_is_stale(existing, ttl_minutes):
        if existing.get("agent") == agent and existing.get("pid") == os.getpid():
            return existing
        raise RuntimeError(
            "Workspace em uso por "
            f"{existing.get('agent', 'agente desconhecido')} desde "
            f"{existing.get('acquired_at', 'horario desconhecido')}: "
            f"{existing.get('activity', 'atividade nao informada')}."
        )
    if existing:
        path.unlink(missing_ok=True)

    payload = {
        "version": 1,
        "agent": agent,
        "activity": activity,
        "pid": os.getpid(),
        "host": socket.gethostname(),
        "acquired_at": now_utc().isoformat(),
        "worktree": str(ROOT),
    }
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2)
        handle.write("\n")
    return payload


def release_lock(agent: str, force: bool = False) -> None:
    path = lock_path()
    existing = read_lock(path)
    if not existing:
        return
    if not force and existing.get("agent") != agent:
        raise RuntimeError(
            f"Lock pertence a {existing.get('agent', 'agente desconhecido')}; "
            "liberacao recusada."
        )
    path.unlink(missing_ok=True)


def ref_exists(ref: str) -> bool:
    return run_git("show-ref", "--verify", "--quiet", ref, check=False).returncode == 0


def is_ancestor(older: str, newer: str) -> bool:
    return run_git("merge-base", "--is-ancestor", older, newer, check=False).returncode == 0


def working_tree_clean() -> bool:
    return not run_git("status", "--porcelain", "--untracked-files=all").stdout.strip()


def ensure_no_operation_in_progress() -> None:
    for marker in ("MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD", "REVERT_HEAD"):
        if git_path(marker).exists():
            raise RuntimeError(f"Operacao Git em andamento detectada: {marker}.")


def preflight(branch: str, remotes: list[str], integrate: bool) -> dict[str, Any]:
    ensure_no_operation_in_progress()
    fetched: list[str] = []
    unavailable: list[str] = []
    refs: list[str] = []
    for remote in remotes:
        result = run_git("fetch", remote, branch, check=False)
        if result.returncode != 0:
            unavailable.append(remote)
            continue
        fetched.append(remote)
        ref = f"refs/remotes/{remote}/{branch}"
        if ref_exists(ref):
            refs.append(ref)

    if not refs:
        raise RuntimeError("Nenhum remoto acessivel para o preflight multiagente.")

    newest = refs[0]
    for candidate in refs[1:]:
        if is_ancestor(newest, candidate):
            newest = candidate
        elif not is_ancestor(candidate, newest):
            raise RuntimeError(
                f"Remotos divergiram entre {newest} e {candidate}; integracao manual sem descarte e obrigatoria."
            )

    head = "HEAD"
    action = "aligned"
    if is_ancestor(head, newest) and not is_ancestor(newest, head):
        if not integrate:
            raise RuntimeError(f"HEAD esta atras de {newest}; execute preflight com --integrate.")
        if not working_tree_clean():
            raise RuntimeError("HEAD esta atras do remoto, mas o worktree possui mudancas locais.")
        run_git("merge", "--ff-only", newest)
        action = f"fast-forward:{newest}"
    elif not is_ancestor(newest, head):
        raise RuntimeError(f"HEAD divergiu de {newest}; integracao manual sem descarte e obrigatoria.")

    return {
        "branch": branch,
        "fetched": fetched,
        "unavailable": unavailable,
        "authoritative_ref": newest,
        "action": action,
        "head": run_git("rev-parse", "HEAD").stdout.strip(),
    }


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description="Coordena agentes e remotos do workspace All-in-One.")
    subcommands = cli.add_subparsers(dest="command", required=True)

    acquire = subcommands.add_parser("acquire")
    acquire.add_argument("--agent", required=True)
    acquire.add_argument("--activity", required=True)
    acquire.add_argument("--ttl-minutes", type=int, default=DEFAULT_TTL_MINUTES)

    release = subcommands.add_parser("release")
    release.add_argument("--agent", required=True)
    release.add_argument("--force", action="store_true")

    subcommands.add_parser("status")

    check = subcommands.add_parser("preflight")
    check.add_argument("--branch", default="main")
    check.add_argument("--remotes", nargs="+", default=["origin", "fork"])
    check.add_argument("--integrate", action="store_true")
    return cli


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "acquire":
            result = acquire_lock(args.agent, args.activity, args.ttl_minutes)
        elif args.command == "release":
            # Higienização mandatória de armazenamento GCP antes de liberar
            hygiene_script = ROOT / "scripts" / "gcp_storage_hygiene.py"
            if hygiene_script.exists():
                subprocess.run([sys.executable, str(hygiene_script)], capture_output=True)
            release_lock(args.agent, args.force)
            result = {"released": True, "agent": args.agent}
        elif args.command == "status":
            result = read_lock() or {"locked": False, "path": str(lock_path())}
        else:
            result = preflight(args.branch, args.remotes, args.integrate)
    except (RuntimeError, subprocess.CalledProcessError, OSError) as exc:
        print(f"Falha no guardiao multiagente: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
