from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCT_FEED = ROOT / "apps/valley/src/components/ProductFeed.tsx"
PRODUCT_VIEWS = ROOT / "apps/valley/src/views/ProductViews.tsx"
PRODUCT_CSS = ROOT / "apps/valley/src/product_feed.css"
MAIN = ROOT / "apps/valley/src/main.tsx"


def test_feed_supports_horizontal_media_carousel_and_product_detail() -> None:
    feed = PRODUCT_FEED.read_text(encoding="utf-8")
    styles = PRODUCT_CSS.read_text(encoding="utf-8")
    main = MAIN.read_text(encoding="utf-8")

    assert "type FeedMedia" in feed
    assert "className='feed-media-carousel'" in feed
    assert "onOpenDetails={() => setDetailProduct(product)}" in feed
    assert "ProductDetailDialog" in feed
    assert "Descrição completa" in feed
    assert "Características e informações" in feed
    assert "scroll-snap-type:x mandatory" in styles
    assert "./product_feed.css" in main


def test_feed_click_does_not_toggle_video_pause() -> None:
    feed = PRODUCT_FEED.read_text(encoding="utf-8")

    assert "controls" not in feed
    assert "onClick={openDetails}" in feed
    assert "onClick={() => video.pause" not in feed
    assert "onClick={event => video.pause" not in feed


def test_marketplace_and_stock_preserve_complete_media_gallery() -> None:
    views = PRODUCT_VIEWS.read_text(encoding="utf-8")

    assert "mediaFrom(item.media, item.image_url)" in views
    assert "Array.isArray(metadata.gallery)" in views
    assert "Array.isArray(payload.gallery)" in views
    assert "Array.isArray(metadata.videos)" in views
    assert "Array.isArray(payload.videos)" in views


def test_supplier_profile_is_public_and_contact_stays_inside_valley() -> None:
    feed = PRODUCT_FEED.read_text(encoding="utf-8")
    views = PRODUCT_VIEWS.read_text(encoding="utf-8")

    assert "Telefone, e-mail, redes sociais" in feed
    assert "somente dentro do aplicativo Valley" in feed
    assert "channel: 'valley_in_app'" in views

    forbidden_supplier_fields = (
        "payload.phone",
        "payload.email",
        "payload.whatsapp",
        "payload.telegram",
        "payload.instagram",
        "payload.facebook",
        "payload.website",
        "item.phone",
        "item.email",
        "item.whatsapp",
        "item.website",
        "metadata.phone",
        "metadata.email",
        "metadata.whatsapp",
        "metadata.website",
    )
    for forbidden in forbidden_supplier_fields:
        assert forbidden not in views
