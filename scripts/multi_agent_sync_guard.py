from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from re import fullmatch
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TTL_MINUTES = 120
GCP_HYGIENE_TIMEOUT_SECONDS = 60


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


def lock_path(scope: str = "workspace") -> Path:
    if not fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", scope):
        raise RuntimeError(
            "Escopo de lock invalido. Use de 1 a 64 caracteres alfanumericos, '.', '_' ou '-'."
        )
    return git_path(f"all-in-one-agent-locks/{scope}.lock")


def now_utc() -> datetime:
    return datetime.now(UTC)


def process_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def read_lock(
    path: Path | None = None, scope: str = "workspace"
) -> dict[str, Any] | None:
    target = path or lock_path(scope)
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
    if now_utc() - acquired_at > timedelta(minutes=ttl_minutes):
        return True
    pid = payload.get("pid")
    host = payload.get("host")
    if isinstance(pid, int) and pid > 0 and host in (None, socket.gethostname()):
        return not process_is_alive(pid)
    return False


def acquire_lock(
    agent: str, activity: str, ttl_minutes: int, scope: str = "workspace"
) -> dict[str, Any]:
    path = lock_path(scope)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_lock(path)
    if existing and not lock_is_stale(existing, ttl_minutes):
        if existing.get("agent") == agent:
            existing.update(
                {
                    "activity": activity,
                    "pid": os.getpid(),
                    "host": socket.gethostname(),
                    "acquired_at": now_utc().isoformat(),
                    "scope": scope,
                }
            )
            path.write_text(
                json.dumps(existing, ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            return existing
        raise RuntimeError(
            f"Escopo '{scope}' em uso por "
            f"{existing.get('agent', 'agente desconhecido')} desde "
            f"{existing.get('acquired_at', 'horario desconhecido')}: "
            f"{existing.get('activity', 'atividade nao informada')}."
        )
    if existing:
        path.unlink(missing_ok=True)

    payload = {
        "version": 2,
        "agent": agent,
        "activity": activity,
        "scope": scope,
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


def release_lock(agent: str, force: bool = False, scope: str = "workspace") -> None:
    path = lock_path(scope)
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
    return (
        run_git("merge-base", "--is-ancestor", older, newer, check=False).returncode
        == 0
    )


def working_tree_clean() -> bool:
    return not run_git("status", "--porcelain", "--untracked-files=all").stdout.strip()


def working_tree_paths() -> set[str]:
    changed = run_git("diff", "--name-only", "HEAD").stdout.splitlines()
    staged = run_git("diff", "--cached", "--name-only").stdout.splitlines()
    untracked = run_git(
        "ls-files", "--others", "--exclude-standard"
    ).stdout.splitlines()
    return set(changed) | set(staged) | set(untracked)


def changed_paths_between(older: str, newer: str) -> set[str]:
    return set(run_git("diff", "--name-only", f"{older}..{newer}").stdout.splitlines())


def ensure_no_operation_in_progress() -> None:
    for marker in (
        "MERGE_HEAD",
        "rebase-merge",
        "rebase-apply",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
    ):
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
            raise RuntimeError(
                f"HEAD esta atras de {newest}; execute preflight com --integrate."
            )
        if not working_tree_clean():
            local_paths = working_tree_paths()
            remote_paths = changed_paths_between(head, newest)
            overlap = sorted(local_paths & remote_paths)
            if overlap:
                preview = ", ".join(overlap[:5])
                suffix = "..." if len(overlap) > 5 else ""
                raise RuntimeError(
                    "HEAD esta atras do remoto e ha sobreposicao com mudancas locais: "
                    f"{preview}{suffix}."
                )
        run_git("merge", "--ff-only", newest)
        action = (
            f"fast-forward:{newest}"
            if working_tree_clean()
            else f"fast-forward-com-mudancas-locais:{newest}"
        )
    elif not is_ancestor(newest, head):
        raise RuntimeError(
            f"HEAD divergiu de {newest}; integracao manual sem descarte e obrigatoria."
        )

    return {
        "branch": branch,
        "fetched": fetched,
        "unavailable": unavailable,
        "authoritative_ref": newest,
        "action": action,
        "head": run_git("rev-parse", "HEAD").stdout.strip(),
    }


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(
        description="Coordena agentes e remotos do workspace All-in-One."
    )
    subcommands = cli.add_subparsers(dest="command", required=True)

    acquire = subcommands.add_parser("acquire")
    acquire.add_argument("--agent", required=True)
    acquire.add_argument("--activity", required=True)
    acquire.add_argument("--ttl-minutes", type=int, default=DEFAULT_TTL_MINUTES)
    acquire.add_argument("--scope", default="workspace")

    release = subcommands.add_parser("release")
    release.add_argument("--agent", required=True)
    release.add_argument("--force", action="store_true")
    release.add_argument("--scope", default="workspace")

    status = subcommands.add_parser("status")
    status.add_argument("--scope", default="workspace")

    check = subcommands.add_parser("preflight")
    check.add_argument("--branch", default="main")
    check.add_argument("--remotes", nargs="+", default=["origin", "fork"])
    check.add_argument("--integrate", action="store_true")
    return cli


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "acquire":
            result = acquire_lock(
                args.agent, args.activity, args.ttl_minutes, args.scope
            )
        elif args.command == "release":
            # Higienização mandatória de armazenamento GCP antes de liberar
            hygiene_script = ROOT / "scripts" / "gcp_storage_hygiene.py"
            if hygiene_script.exists():
                try:
                    subprocess.run(
                        [sys.executable, str(hygiene_script)],
                        capture_output=True,
                        timeout=GCP_HYGIENE_TIMEOUT_SECONDS,
                    )
                except subprocess.TimeoutExpired:
                    # A higiene externa não pode manter o workspace bloqueado
                    # indefinidamente. O próximo ciclo tentará executá-la de novo.
                    pass
            release_lock(args.agent, args.force, args.scope)
            result = {"released": True, "agent": args.agent, "scope": args.scope}
        elif args.command == "status":
            result = read_lock(scope=args.scope) or {
                "locked": False,
                "path": str(lock_path(args.scope)),
                "scope": args.scope,
            }
        else:
            result = preflight(args.branch, args.remotes, args.integrate)
    except (RuntimeError, subprocess.CalledProcessError, OSError) as exc:
        print(f"Falha no guardiao multiagente: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
