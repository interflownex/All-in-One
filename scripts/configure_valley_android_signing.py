#!/usr/bin/env python3
"""Cria e valida a assinatura release local do Valley Android fora do Git."""

from __future__ import annotations

import argparse
import os
import secrets
import stat
import string
import subprocess
from pathlib import Path


DEFAULT_DIR = Path.home() / ".config" / "all-in-one"
DEFAULT_KEYSTORE = DEFAULT_DIR / "valley-release.jks"
DEFAULT_PROPERTIES = DEFAULT_DIR / "valley-release.properties"
DEFAULT_ALIAS = "valley-release"


def strong_password(length: int = 32) -> str:
    if length < 4:
        raise ValueError("A senha deve ter pelo menos quatro caracteres.")
    punctuation = "-_.@"
    alphabet = string.ascii_letters + string.digits + punctuation
    characters = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(punctuation),
    ]
    characters.extend(secrets.choice(alphabet) for _ in range(length - len(characters)))
    secrets.SystemRandom().shuffle(characters)
    return "".join(characters)


def write_private(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(content)


def validate_private(path: Path) -> None:
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise RuntimeError(f"Permissoes inseguras em {path}: esperado 600, obtido {mode:o}.")


def create_signing_material(keystore: Path, properties: Path, alias: str) -> None:
    if keystore.exists() or properties.exists():
        raise RuntimeError("Assinatura release ja existe; use --check para validar sem sobrescrever.")
    store_password = strong_password()
    key_password = strong_password()
    keystore.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    subprocess.run(
        [
            "keytool",
            "-genkeypair",
            "-v",
            "-keystore",
            str(keystore),
            "-storetype",
            "JKS",
            "-storepass",
            store_password,
            "-keypass",
            key_password,
            "-alias",
            alias,
            "-keyalg",
            "RSA",
            "-keysize",
            "4096",
            "-validity",
            "10000",
            "-dname",
            "CN=Valley Consumer, OU=Mobile, O=All-in-One, C=BR",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    keystore.chmod(0o600)
    write_private(
        properties,
        "\n".join(
            (
                f"storeFile={keystore}",
                f"storePassword={store_password}",
                f"keyAlias={alias}",
                f"keyPassword={key_password}",
                "",
            )
        ),
    )


def validate(keystore: Path, properties: Path) -> None:
    if not keystore.is_file() or not properties.is_file():
        raise RuntimeError("Keystore ou arquivo de propriedades release ausente.")
    validate_private(keystore)
    validate_private(properties)
    values = dict(
        line.split("=", 1)
        for line in properties.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    )
    required = {"storeFile", "storePassword", "keyAlias", "keyPassword"}
    missing = sorted(required - values.keys())
    if missing:
        raise RuntimeError("Propriedades release ausentes: " + ", ".join(missing))
    subprocess.run(
        [
            "keytool",
            "-list",
            "-keystore",
            str(keystore),
            "-storepass",
            values["storePassword"],
            "-alias",
            values["keyAlias"],
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--create", action="store_true", help="Cria a assinatura quando ausente.")
    parser.add_argument("--check", action="store_true", help="Valida a assinatura existente.")
    parser.add_argument("--keystore", type=Path, default=DEFAULT_KEYSTORE)
    parser.add_argument("--properties", type=Path, default=DEFAULT_PROPERTIES)
    parser.add_argument("--alias", default=DEFAULT_ALIAS)
    args = parser.parse_args()
    if not args.create and not args.check:
        parser.error("Informe --create ou --check.")
    if args.create:
        create_signing_material(args.keystore, args.properties, args.alias)
    validate(args.keystore, args.properties)
    print(f"Assinatura Valley validada: keystore={args.keystore} alias={args.alias}")
    print(f"Propriedades protegidas: {args.properties}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
