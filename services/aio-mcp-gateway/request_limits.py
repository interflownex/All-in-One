from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestBodyLimitMiddleware:
    """Reject oversized MCP request bodies before protocol parsing."""

    def __init__(self, app: ASGIApp, max_body_bytes: int) -> None:
        if max_body_bytes <= 0:
            raise ValueError("max_body_bytes deve ser maior que zero")
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http" or not _is_mcp_path(scope):
            await self.app(scope, receive, send)
            return

        content_length = _content_length(scope)
        if content_length is None:
            await _send_json(
                send,
                400,
                {"error": "invalid_content_length"},
            )
            return
        if content_length > self.max_body_bytes:
            await _send_too_large(send, self.max_body_bytes)
            return

        buffered: list[Message] = []
        total = 0
        while True:
            message = await receive()
            buffered.append(message)
            if message["type"] == "http.disconnect":
                await self.app(scope, _replay(buffered, receive), send)
                return
            if message["type"] != "http.request":
                continue
            total += len(message.get("body", b""))
            if total > self.max_body_bytes:
                await _send_too_large(send, self.max_body_bytes)
                return
            if not message.get("more_body", False):
                break

        await self.app(scope, _replay(buffered, receive), send)


def _is_mcp_path(scope: Scope) -> bool:
    path = str(scope.get("path", ""))
    return path == "/mcp" or path.startswith("/mcp/")


def _content_length(scope: Scope) -> int | None:
    raw_value: str | None = None
    for key, value in scope.get("headers", []):
        if key.lower() == b"content-length":
            raw_value = value.decode("ascii", errors="strict").strip()
            break
    if raw_value is None or raw_value == "":
        return 0
    try:
        parsed = int(raw_value)
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


def _replay(messages: list[Message], fallback: Receive) -> Receive:
    index = 0

    async def receive() -> Message:
        nonlocal index
        if index < len(messages):
            message = messages[index]
            index += 1
            return message
        return await fallback()

    return receive


async def _send_too_large(send: Send, max_body_bytes: int) -> None:
    await _send_json(
        send,
        413,
        {
            "error": "request_body_too_large",
            "max_body_bytes": max_body_bytes,
        },
    )


async def _send_json(
    send: Send,
    status: int,
    payload: Mapping[str, Any],
) -> None:
    body = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json; charset=utf-8"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})
