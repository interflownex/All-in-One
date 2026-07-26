from __future__ import annotations

import json
from pathlib import Path

import pytest

from modules.shared.innovation_runtime import (
    DEFAULT_CATALOG_PATH,
    InnovationCatalogError,
    get_innovation,
    innovation_enabled,
    innovation_summary,
    load_innovation_catalog,
    validate_innovation_catalog,
)


def test_wave_covers_every_active_module_once_and_excludes_vision() -> None:
    definitions = load_innovation_catalog()

    assert len(definitions) == 24
    assert len({item.module for item in definitions}) == 24
    assert "vision" not in {item.module for item in definitions}
    assert {item.id for item in definitions} == {
        *(f"INNOV-{number:03d}" for number in range(1, 23)),
        "INNOV-024",
        "INNOV-025",
    }


def test_feature_flags_are_safe_by_default_and_accept_explicit_override() -> None:
    initiative = get_innovation("innov-001")

    assert innovation_enabled(initiative.id, {}) is False
    assert innovation_enabled(
        initiative.id,
        {initiative.environment_variable: "true"},
    ) is True
    assert innovation_enabled(
        initiative.id,
        {initiative.environment_variable: "off"},
    ) is False

    with pytest.raises(InnovationCatalogError, match="Valor invalido"):
        innovation_enabled(
            initiative.id,
            {initiative.environment_variable: "talvez"},
        )


def test_catalog_rejects_any_attempt_to_restore_vision() -> None:
    payload = json.loads(Path(DEFAULT_CATALOG_PATH).read_text(encoding="utf-8"))
    payload["initiatives"][0]["module"] = "vision"

    with pytest.raises(InnovationCatalogError, match="Vision nao pode"):
        validate_innovation_catalog(payload)


def test_summary_reports_priorities_and_no_automatic_activation() -> None:
    summary = innovation_summary()

    assert summary["wave_id"] == "innovation-wave-001"
    assert summary["module_count"] == 24
    assert sum(summary["priorities"].values()) == 24
    assert summary["enabled"] == []
    assert summary["forbidden_modules"] == ["vision"]
