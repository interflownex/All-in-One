from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

DEFAULT_COMMANDS = (
    (sys.executable, "scripts/scaffold_modules.py", "--check"),
    (sys.executable, "scripts/generate_domain_event_fixtures.py", "--check"),
    (sys.executable, "scripts/validate_openapi.py"),
    (sys.executable, "scripts/validate_repository.py"),
)


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(
            "Este comando precisa ser executado dentro de um repositorio Git."
        )
    return Path(result.stdout.strip())


def git_status(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return result.stdout.splitlines()


def run_command(root: Path, command: tuple[str, ...]) -> None:
    print("Executando: " + " ".join(command))
    subprocess.run(command, cwd=root, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Falha se scaffold/validadores alterarem a arvore de trabalho."
    )
    parser.add_argument(
        "--command",
        action="append",
        dest="commands",
        help="Comando adicional/substituto. Pode ser informado multiplas vezes.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    commands = (
        tuple(tuple(shlex.split(command)) for command in args.commands)
        if args.commands
        else DEFAULT_COMMANDS
    )

    before = git_status(root)
    for command in commands:
        run_command(root, command)
    after = git_status(root)

    if before != after:
        print("Estado antes:")
        print("\n".join(before) or "<limpo>")
        print("Estado depois:")
        print("\n".join(after) or "<limpo>")
        print(
            "Artefatos gerados ou validadores alteraram a arvore de trabalho. "
            "Execute, revise e commite os resultados.",
            file=sys.stderr,
        )
        return 1

    print("Gate de artefatos gerados aprovado: arvore de trabalho preservada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
