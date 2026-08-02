from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_gke_workflow_is_manual_in_local_first_mode() -> None:
    workflow = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "confirm_gcp_billing_enabled" in workflow
    assert 'GOOGLE_CLOUD_ENABLED: "false"' in workflow
    assert 'GOOGLE_CLOUD_ENABLED: "true"' in workflow
    assert "inputs.confirm_gcp_billing_enabled == true" in workflow
    assert "inputs.confirm_gcp_billing_enabled != true" in workflow
    assert "gcloud container clusters get-credentials" in workflow
    assert "  push:" not in workflow
    assert "branches: [main]" not in workflow
