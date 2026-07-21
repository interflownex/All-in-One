from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from modules.shared.units_tax import ConversionRule, TaxRule, calculate_tax, convert_quantity


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "database/postgres/migrations/025_units_tax_governance.sql"
ROLLBACK = ROOT / "database/postgres/rollbacks/025_units_tax_governance.down.sql"


def active_window() -> tuple[datetime, datetime]:
    now = datetime.now(UTC)
    return now - timedelta(days=1), now + timedelta(days=1)


def test_units_tax_migration_implements_every_proposed_entity_and_rollback() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    rollback = ROLLBACK.read_text(encoding="utf-8")
    entities = {
        "stock.measurement_units",
        "stock.product_units",
        "stock.product_unit_conversions",
        "stock.stock_movements",
        "stock.product_lots",
        "stock.product_serials",
        "erp.fiscal_profiles",
        "erp.fiscal_rules",
        "erp.product_tax_classifications",
        "erp.product_fiscal_assignments",
        "erp.tax_calculation_snapshots",
    }

    assert all(f"CREATE TABLE IF NOT EXISTS {entity}" in migration for entity in entities)
    assert all(f"DROP TABLE IF EXISTS {entity}" in rollback for entity in entities)
    assert "DOUBLE PRECISION" not in migration and " REAL " not in migration
    assert "conversion_factor_snapshot NUMERIC" in migration
    assert "input_hash VARCHAR(128) NOT NULL" in migration


def test_units_tax_physical_catalog_covers_every_proposed_field() -> None:
    proposal = json.loads(
        (ROOT / "config/data_audit/product_units_tax_model_proposal.json").read_text(encoding="utf-8")
    )
    dictionary = json.loads(
        (ROOT / "docs/data-audit/artifacts/dicionario_de_dados.json").read_text(encoding="utf-8")
    )
    physical: dict[str, set[str]] = {}
    for field in dictionary["fields"]:
        physical.setdefault(f'{field["schema"]}.{field["table"]}', set()).add(field["physical_name"])

    for entity, fields in proposal["measurement_entities"].items():
        assert set(fields) <= physical[f"stock.{entity}"]
    for entity, fields in proposal["fiscal_entities"].items():
        assert set(fields) <= physical[f"erp.{entity}"]


def test_decimal_conversion_preserves_precision_and_rounding() -> None:
    start, end = active_window()
    rule = ConversionRule(
        multiplier="1000",
        divisor="3",
        precision=4,
        rounding_mode="half_up",
        source_dimension="mass",
        target_dimension="mass",
        effective_from=start,
        effective_to=end,
        approved=True,
    )

    assert convert_quantity("2.5", rule) == Decimal("833.3333")


def test_cross_dimension_conversion_requires_positive_density() -> None:
    start, end = active_window()
    rule = ConversionRule(
        multiplier="1",
        divisor="1",
        precision=3,
        rounding_mode="half_even",
        source_dimension="volume",
        target_dimension="mass",
        effective_from=start,
        effective_to=end,
        approved=True,
    )

    with pytest.raises(ValueError, match="densidade"):
        convert_quantity("2", rule)


def test_conversion_rejects_float_unapproved_and_expired_rules() -> None:
    start, end = active_window()
    base = dict(
        multiplier="1",
        divisor="1",
        precision=2,
        rounding_mode="half_up",
        source_dimension="unit",
        target_dimension="unit",
        effective_from=start,
        effective_to=end,
    )

    with pytest.raises(TypeError, match="Float"):
        convert_quantity(1.2, ConversionRule(**base, approved=True))
    with pytest.raises(ValueError, match="aprovada"):
        convert_quantity("1", ConversionRule(**base, approved=False))
    with pytest.raises(ValueError, match="vigencia"):
        convert_quantity("1", ConversionRule(**base, approved=True), at=end)


def test_tax_calculation_uses_reduction_rate_and_declared_rounding() -> None:
    start, end = active_window()
    rule = TaxRule(
        rate="0.18",
        base_reduction="0.10",
        precision=2,
        rounding_mode="half_up",
        legal_basis="Lei de teste versionada",
        effective_from=start,
        effective_to=end,
        approved=True,
    )

    base, amount = calculate_tax("100.00", rule)

    assert base == Decimal("90.00")
    assert amount == Decimal("16.20")


def test_tax_calculation_rejects_missing_governance() -> None:
    start, end = active_window()
    rule = TaxRule(
        rate="0.18",
        base_reduction="0",
        precision=2,
        rounding_mode="half_up",
        legal_basis="",
        effective_from=start,
        effective_to=end,
        approved=True,
    )

    with pytest.raises(ValueError, match="Fundamento"):
        calculate_tax("100", rule)
