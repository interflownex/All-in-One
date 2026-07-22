"""Contrato seguro para mídia pública do catálogo Valley via CDN."""

from __future__ import annotations

import os
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import quote, urlparse

CDN_ENV = "VALLEY_MEDIA_CDN_BASE_URL"
IMAGE_EXTENSIONS = {".avif", ".jpeg", ".jpg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".m4v", ".mp4", ".webm"}


def configured_cdn_base() -> str | None:
    raw = os.getenv(CDN_ENV, "").strip().rstrip("/")
    if not raw:
        return None
    parsed = urlparse(raw)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise RuntimeError(
            f"{CDN_ENV} deve ser uma origem HTTPS sem credenciais, query ou fragmento"
        )
    return raw


def normalize_offer_media(offer: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(offer)
    base = configured_cdn_base()
    media: list[dict[str, str]] = []
    if base:
        for item in offer.get("media") or []:
            candidate = _normalize_item(item, base)
            if candidate and candidate not in media:
                media.append(candidate)
    normalized["media"] = media
    metadata: dict[str, str] = {}
    for item in media:
        metadata.setdefault(f"{item['type']}_url", item["url"])
    normalized["metadata"] = metadata
    return normalized


def _normalize_item(item: Any, base: str) -> dict[str, str] | None:
    if isinstance(item, str):
        key = item
        declared_type = ""
    elif isinstance(item, dict):
        key = str(item.get("key") or item.get("path") or item.get("url") or "")
        declared_type = str(item.get("type") or "").lower()
    else:
        return None
    key = key.strip()
    if not key:
        return None
    parsed = urlparse(key)
    if parsed.scheme or parsed.netloc:
        if not key.startswith(f"{base}/"):
            return None
        key = key[len(base) + 1 :]
    clean_path = PurePosixPath(key)
    if clean_path.is_absolute() or ".." in clean_path.parts:
        return None
    suffix = clean_path.suffix.lower()
    inferred_type = (
        "image"
        if suffix in IMAGE_EXTENSIONS
        else "video"
        if suffix in VIDEO_EXTENSIONS
        else ""
    )
    media_type = declared_type if declared_type in {"image", "video"} else inferred_type
    if (
        not media_type
        or (media_type == "image" and suffix not in IMAGE_EXTENSIONS)
        or (media_type == "video" and suffix not in VIDEO_EXTENSIONS)
    ):
        return None
    encoded_key = "/".join(quote(part, safe="-._~") for part in clean_path.parts)
    return {"type": media_type, "url": f"{base}/{encoded_key}"}
