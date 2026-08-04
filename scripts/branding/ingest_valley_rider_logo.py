#!/usr/bin/env python3
"""Ingere a logomarca oficial Valley Rider sem alterar um único byte."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import struct
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SHA256 = "f5fba898ee9c660a35e359b8968b1b7d7256d7ded7434e34d1abd601e609db73"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
DESTINATIONS = (
    ROOT / "assets" / "brand" / "valley-riders-logo-official.png",
    ROOT / "apps" / "valley_rider" / "public" / "brand" / "valley-riders-logo-official.png",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_png(path: Path) -> tuple[int, int, int]:
    with path.open("rb") as handle:
        signature = handle.read(8)
        if signature != b"\x89PNG\r\n\x1a\n":
            raise ValueError("O arquivo não possui assinatura PNG válida.")
        length = struct.unpack(">I", handle.read(4))[0]
        chunk_type = handle.read(4)
        if chunk_type != b"IHDR" or length != 13:
            raise ValueError("Cabeçalho IHDR inválido.")
        width, height, bit_depth, color_type, _, _, _ = struct.unpack(">IIBBBBB", handle.read(13))
    return width, height, color_type


def atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as temporary:
        temp_path = Path(temporary.name)
    try:
        shutil.copyfile(source, temp_path)
        os.chmod(temp_path, 0o600)
        temp_path.replace(destination)
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="PNG oficial baixado do Drive.")
    parser.add_argument("--verify-only", action="store_true", help="Valida sem copiar.")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {source}")

    actual_sha = sha256(source)
    if actual_sha != EXPECTED_SHA256:
        raise ValueError(f"SHA-256 divergente: {actual_sha}")

    width, height, color_type = inspect_png(source)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise ValueError(f"Dimensões divergentes: {width}x{height}")
    if color_type not in (4, 6):
        raise ValueError("A logomarca deve preservar canal alfa/transparência.")

    if args.verify_only:
        print(f"OK: marca oficial validada ({width}x{height}, SHA-256 {actual_sha}).")
        return 0

    for destination in DESTINATIONS:
        atomic_copy(source, destination)
        copied_sha = sha256(destination)
        if copied_sha != EXPECTED_SHA256:
            raise RuntimeError(f"Falha de integridade após copiar para {destination}")
        print(f"OK: {destination.relative_to(ROOT)}")

    print("A arte foi copiada sem recompressão, recorte, recoloração ou alteração de bytes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
