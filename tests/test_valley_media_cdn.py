from __future__ import annotations

from modules.shared.media_cdn import normalize_offer_media


def test_media_keys_are_normalized_to_configured_https_cdn(monkeypatch) -> None:
    monkeypatch.setenv("VALLEY_MEDIA_CDN_BASE_URL", "https://media.valley.example/v1")

    offer = normalize_offer_media(
        {"media": ["offers/item 1.webp", {"path": "videos/demo.mp4", "type": "video"}]}
    )

    assert offer["metadata"] == {
        "image_url": "https://media.valley.example/v1/offers/item%201.webp",
        "video_url": "https://media.valley.example/v1/videos/demo.mp4",
    }


def test_media_rejects_external_urls_traversal_and_unknown_formats(monkeypatch) -> None:
    monkeypatch.setenv("VALLEY_MEDIA_CDN_BASE_URL", "https://media.valley.example")

    offer = normalize_offer_media(
        {
            "media": [
                "https://tracker.example/pixel.png",
                "../secret.png",
                "offers/script.svg",
            ]
        }
    )

    assert offer["media"] == []
    assert offer["metadata"] == {}
