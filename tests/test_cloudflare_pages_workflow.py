from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cloudflare_pages_workflow_is_explicit_and_blocking() -> None:
    workflow = (ROOT / ".github" / "workflows" / "cloudflare-pages.yml").read_text(
        encoding="utf-8"
    )

    assert 'WRANGLER_VERSION: "4.118.0"' in workflow
    assert 'CLOUDFLARE_PAGES_PROJECT: "all-in-one-web"' in workflow
    assert "if: ${{ vars.ENABLE_CLOUDFLARE_PAGES == 'true' }}" in workflow
    assert "CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}" in workflow
    assert "CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}" in workflow
    assert "VITE_API_HUB_URL: ${{ vars.VITE_API_HUB_URL }}" in workflow
    assert "test -n \"$CLOUDFLARE_API_TOKEN\"" in workflow
    assert "test -n \"$CLOUDFLARE_ACCOUNT_ID\"" in workflow
    assert "test -n \"$VITE_API_HUB_URL\"" in workflow
    assert "uses: actions/checkout@v6" in workflow
    assert "uses: cloudflare/wrangler-action@v4" in workflow
    assert "wranglerVersion: ${{ env.WRANGLER_VERSION }}" in workflow
    assert "curl --fail --silent --show-error" in workflow
    assert "HAS_TELEGRAM_DELIVERY" in workflow
    assert "deploy_enabled=false" not in workflow
    assert "actions/checkout@v4" not in workflow
