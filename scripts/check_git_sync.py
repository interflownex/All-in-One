#!/usr/bin/env python3
"""Valida sincronizacao da branch atual com os remotos configurados."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def git_output(args: list[str]) -> str:
    return git(args).stdout.strip()


def git_path_exists(path: str) -> bool:
    resolved = git_output(["rev-parse", "--git-path", path])
    return Path(resolved).exists()


def current_branch(explicit_branch: str | None) -> str:
    if explicit_branch:
        return explicit_branch
    branch = git_output(["branch", "--show-current"])
    if branch:
        return branch
    branch = os.environ.get("GITHUB_REF_NAME", "").strip()
    if branch:
        return branch
    raise RuntimeError("Nao foi possivel identificar a branch atual. Informe --branch.")


def validate(args: argparse.Namespace) -> int:
    for state_path in ("MERGE_HEAD", "rebase-merge", "rebase-apply"):
        if git_path_exists(state_path):
            raise RuntimeError("Verificacao bloqueada: ha merge ou rebase em andamento.")

    branch = current_branch(args.branch)
    status = git_output(["status", "--porcelain"])
    if status and not args.allow_dirty:
        raise RuntimeError("A arvore de trabalho possui alteracoes locais. Use --allow-dirty apenas para diagnostico.")

    available_remotes = set(git_output(["remote"]).splitlines())
    checked = 0
    problems: list[str] = []

    for remote in args.remotes:
        if remote not in available_remotes:
            print(f"WARNING: Remoto ausente neste checkout: {remote}", file=sys.stderr)
            continue

        if not args.no_fetch:
            fetch = git(["fetch", remote, branch, "--prune"], check=False)
            if fetch.returncode != 0:
                problems.append(f"Fetch falhou para {remote}/{branch}: {fetch.stdout.strip()}")
                continue

        verify = git(["rev-parse", "--verify", f"{remote}/{branch}"], check=False)
        if verify.returncode != 0:
            problems.append(f"Referencia remota inexistente: {remote}/{branch}.")
            continue

        counts = git_output(["rev-list", "--left-right", "--count", f"{remote}/{branch}...HEAD"]).split()
        behind, ahead = int(counts[0]), int(counts[1])
        checked += 1

        if behind > 0:
            problems.append(f"Branch local esta {behind} commit(s) atras de {remote}/{branch}.")
        if ahead > 0 and not args.allow_ahead:
            problems.append(f"Branch local esta {ahead} commit(s) a frente de {remote}/{branch}.")

        print(f"{remote}/{branch}: behind={behind} ahead={ahead}")

    if checked == 0:
        raise RuntimeError(f"Nenhum remoto verificavel encontrado para a branch {branch}.")
    if problems:
        raise RuntimeError("Divergencia Git detectada:\n- " + "\n- ".join(problems))

    print(f"Sincronizacao Git validada para {checked} remoto(s).")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch")
    parser.add_argument("--remotes", nargs="+", default=["origin", "fork"])
    parser.add_argument("--allow-ahead", action="store_true")
    parser.add_argument("--allow-dirty", action="store_true")
    parser.add_argument("--no-fetch", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return validate(args)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
