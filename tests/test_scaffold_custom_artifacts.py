from __future__ import annotations

from scripts.check_scaffold_modules import CUSTOMIZED_ARTIFACTS, STOCK_OPENAPI
from scripts.scaffold_modules import render_main


def test_scaffold_preserves_live_app_shell_artifacts() -> None:
    expected = {
        "modules/permissions/tests/test_create_flow.py",
        "apps/all-in-one-business/README.md",
        "apps/all-in-one-business/STATUS.md",
        "apps/all-in-one-health/README.md",
        "apps/all-in-one-health/STATUS.md",
        "apps/all-in-one-mobility/README.md",
        "apps/all-in-one-mobility/STATUS.md",
        "apps/all-in-one-riders/README.md",
        "apps/all-in-one-riders/STATUS.md",
        "apps/all-in-one-services/README.md",
        "apps/all-in-one-services/STATUS.md",
        "apps/all-in-one-user/STATUS.md",
    }

    assert expected <= CUSTOMIZED_ARTIFACTS


def test_scaffold_preserves_specialized_stock_openapi() -> None:
    assert STOCK_OPENAPI == "modules/stock/OPENAPI.yaml"
    assert STOCK_OPENAPI in CUSTOMIZED_ARTIFACTS


def test_scaffold_includes_commercial_routers() -> None:
    assert "business.commercial_routes" in render_main("business")
    assert "bi.commercial_routes" in render_main("bi")
    assert "crm.commercial_routes" in render_main("crm")
