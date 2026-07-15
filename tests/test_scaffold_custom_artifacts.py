from __future__ import annotations

from scripts.scaffold_modules import CUSTOMIZED_ARTIFACTS


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
