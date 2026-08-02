from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cloudflare_pages_workflow_is_secret_gated() -> None:
    workflow = (ROOT / ".github" / "workflows" / "cloudflare-pages.yml").read_text(
        encoding="utf-8"
    )

    assert 'WRANGLER_VERSION: "4.118.0"' in workflow
    assert 'wranglerVersion: ${{ env.WRANGLER_VERSION }}' in workflow
    assert "HAS_CLOUDFLARE_API_TOKEN" in workflow
    assert "HAS_CLOUDFLARE_ACCOUNT_ID" in workflow
    assert "deploy_enabled=true" in workflow
    assert "deploy_enabled=false" in workflow
    assert "if: steps.credentials.outputs.deploy_enabled == 'true'" in workflow
    assert "HAS_TELEGRAM_DELIVERY" in workflow
    assert 'wranglerVersion: "4.112.0"' not in workflow
