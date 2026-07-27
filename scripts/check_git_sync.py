#!/usr/bin/env python3
"""Valida sincronizacao da branch atual com os remotos configurados."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Comparison:
    label: str
    behind: int
    ahead: int


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


def is_pull_request_event() -> bool:
    return os.environ.get("GITHUB_EVENT_NAME", "").strip() == "pull_request"


def current_branch(explicit_branch: str | None) -> str:
    if explicit_branch:
        return explicit_branch
    upstream = git(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        check=False,
    )
    if upstream.returncode == 0:
        upstream_ref = upstream.stdout.strip()
        if "/" in upstream_ref:
            return upstream_ref.split("/", 1)[1]
    branch = git_output(["branch", "--show-current"])
    if branch:
        return branch
    if is_pull_request_event():
        base_ref = os.environ.get("GITHUB_BASE_REF", "").strip()
        if base_ref:
            return base_ref
    branch = os.environ.get("GITHUB_REF_NAME", "").strip()
    if branch:
        return branch
    raise RuntimeError("Nao foi possivel identificar a branch atual. Informe --branch.")


def parse_commit_parents(commit_text: str) -> tuple[str, ...]:
    parents: list[str] = []
    for line in commit_text.splitlines():
        if not line.startswith("parent "):
            continue
        _, sha = line.split(maxsplit=1)
        sha = sha.strip()
        if len(sha) == 40 and all(character in "0123456789abcdef" for character in sha):
            parents.append(sha)
    return tuple(parents)


def github_pull_request_base(branch: str) -> str | None:
    """Resolve a base do merge temporario criado pelo checkout de Pull Request.

    Em checkouts rasos, ``rev-list`` respeita a fronteira shallow e pode omitir os
    pais, mesmo quando os identificadores permanecem no objeto do commit. Por
    isso, o cabecalho bruto de ``HEAD`` e lido com ``cat-file``. O fallback so
    vale para um evento de Pull Request cuja base declarada coincide com a branch
    solicitada e cujo ``HEAD`` possui exatamente dois pais.
    """

    base_ref = os.environ.get("GITHUB_BASE_REF", "").strip()
    if not is_pull_request_event() or base_ref != branch:
        return None

    commit = git(["cat-file", "-p", "HEAD"], check=False)
    if commit.returncode != 0:
        return None
    parents = parse_commit_parents(commit.stdout)
    if len(parents) != 2:
        return None
    return parents[0]


def rev_list_comparison(ref: str) -> Comparison:
    counts = git_output(
        ["rev-list", "--left-right", "--count", f"{ref}...HEAD"]
    ).split()
    return Comparison(label=ref, behind=int(counts[0]), ahead=int(counts[1]))


def comparison(remote: str, branch: str, *, no_fetch: bool) -> Comparison | None:
    remote_ref = f"{remote}/{branch}"
    verify = git(["rev-parse", "--verify", remote_ref], check=False)
    if verify.returncode == 0:
        return rev_list_comparison(remote_ref)

    if not no_fetch:
        return None

    base_sha = github_pull_request_base(branch)
    if not base_sha:
        return None

    print(
        "WARNING: Referencia remota ausente no checkout raso do PR; "
        f"usando o primeiro pai {base_sha} como base declarada de {remote_ref}.",
        file=sys.stderr,
    )
    # O HEAD do checkout de Pull Request e um merge sintetico criado pelo GitHub.
    # Esse commit nao pertence a branch proposta e, portanto, nao deve ser contado
    # como divergencia "ahead". A presenca do primeiro pai, combinada com
    # GITHUB_BASE_REF, comprova que o merge foi construido sobre a base solicitada.
    # Fora desse contexto estrito, nenhuma contagem e inferida.
    return Comparison(label=f"pull-request-base:{base_sha}", behind=0, ahead=0)


def validate(args: argparse.Namespace) -> int:
    for state_path in ("MERGE_HEAD", "rebase-merge", "rebase-apply"):
        if git_path_exists(state_path):
            raise RuntimeError(
                "Verificacao bloqueada: ha merge ou rebase em andamento."
            )

    branch = current_branch(args.branch)
    status = git_output(["status", "--porcelain"])
    if status and not args.allow_dirty:
        raise RuntimeError(
            "A arvore de trabalho possui alteracoes locais. Use --allow-dirty "
            "apenas para diagnostico."
        )

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
                problems.append(
                    f"Fetch falhou para {remote}/{branch}: {fetch.stdout.strip()}"
                )
                continue

        result = comparison(remote, branch, no_fetch=args.no_fetch)
        if result is None:
            problems.append(f"Referencia remota inexistente: {remote}/{branch}.")
            continue

        checked += 1
        if result.behind > 0:
            problems.append(
                f"Branch local esta {result.behind} commit(s) atras de {remote}/{branch}."
            )
        if result.ahead > 0 and not args.allow_ahead:
            problems.append(
                f"Branch local esta {result.ahead} commit(s) a frente de {remote}/{branch}."
            )

        print(
            f"{remote}/{branch}: behind={result.behind} "
            f"ahead={result.ahead} ref={result.label}"
        )

    if checked == 0:
        raise RuntimeError(
            f"Nenhum remoto verificavel encontrado para a branch {branch}."
        )
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
