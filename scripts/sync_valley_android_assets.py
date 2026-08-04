#!/usr/bin/env python3
"""Sincroniza o build web Valley com os assets Android de forma determinística."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "apps/valley/dist"
DEFAULT_TARGET = ROOT / "apps/valley-android/app/src/main/assets/valley"
RASTER_BRAND_FILES = (Path("assets/brand/favicon-valley.png"),)
TEXT_SUFFIXES = {".html", ".css", ".js", ".json", ".svg", ".webmanifest"}


def _text_payload(root: Path) -> str:
    chunks: list[str] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


def sync_assets(source: Path, target: Path) -> list[Path]:
    if not (source / "index.html").is_file():
        raise FileNotFoundError(f"Build Valley inválido ou ausente: {source}")

    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)

    removed: list[Path] = []
    payload = _text_payload(target)
    for relative in RASTER_BRAND_FILES:
        candidate = target / relative
        if not candidate.exists():
            continue
        if relative.name in payload or relative.as_posix() in payload:
            raise RuntimeError(
                f"Ativo raster ainda referenciado e não pode ser removido: {relative}"
            )
        candidate.unlink()
        removed.append(relative)

    return removed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    removed = sync_assets(args.source.resolve(), args.target.resolve())
    print(f"Assets Valley sincronizados em {args.target.resolve()}.")
    for relative in removed:
        print(f"Ativo raster redundante removido do bundle Android: {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
