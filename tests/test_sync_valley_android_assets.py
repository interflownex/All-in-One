from __future__ import annotations

from pathlib import Path

import pytest

from scripts.sync_valley_android_assets import sync_assets


def _write_build(root: Path, *, reference_png: bool) -> None:
    (root / "assets/brand").mkdir(parents=True)
    (root / "index.html").write_text(
        '<link rel="icon" href="/assets/brand/favicon-valley.svg">'
        + ('<img src="/assets/brand/favicon-valley.png">' if reference_png else ""),
        encoding="utf-8",
    )
    (root / "assets/brand/favicon-valley.svg").write_text("<svg></svg>", encoding="utf-8")
    (root / "assets/brand/favicon-valley.png").write_bytes(b"png-placeholder")


def test_sync_removes_unreferenced_raster_brand_asset(tmp_path: Path) -> None:
    source = tmp_path / "dist"
    target = tmp_path / "android"
    _write_build(source, reference_png=False)

    removed = sync_assets(source, target)

    assert removed == [Path("assets/brand/favicon-valley.png")]
    assert not (target / "assets/brand/favicon-valley.png").exists()
    assert (target / "assets/brand/favicon-valley.svg").is_file()


def test_sync_fails_when_raster_brand_asset_is_referenced(tmp_path: Path) -> None:
    source = tmp_path / "dist"
    target = tmp_path / "android"
    _write_build(source, reference_png=True)

    with pytest.raises(RuntimeError, match="Ativo raster ainda referenciado"):
        sync_assets(source, target)
