from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from starlette.types import Message

SERVICE_ROOT = Path(__file__).resolve().parents[1]
SERVICE_PATH = str(SERVICE_ROOT)
if SERVICE_PATH not in sys.path:
    sys.path.insert(0, SERVICE_PATH)

from request_limits import RequestBodyLimitMiddleware  # noqa: E402


async def _echo_body(request: Request) -> JSONResponse:
    body = await request.body()
    return JSONResponse({"size": len(body)})


def _app(limit: int) -> RequestBodyLimitMiddleware:
    return RequestBodyLimitMiddleware(
        Starlette(routes=[Route("/mcp", _echo_body, methods=["POST"])]),
        max_body_bytes=limit,
    )


def test_body_at_limit_reaches_application() -> None:
    with TestClient(_app(4)) as client:
        response = client.post("/mcp", content=b"1234")

    assert response.status_code == 200
    assert response.json() == {"size": 4}


def test_content_length_over_limit_returns_413() -> None:
    with TestClient(_app(3)) as client:
        response = client.post("/mcp", content=b"1234")

    assert response.status_code == 413
    assert response.json() == {
        "error": "request_body_too_large",
        "max_body_bytes": 3,
    }


def test_invalid_content_length_returns_400() -> None:
    scope: dict[str, Any] = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/mcp",
        "raw_path": b"/mcp",
        "query_string": b"",
        "root_path": "",
        "headers": [(b"content-length", b"not-an-integer")],
        "client": ("127.0.0.1", 1234),
        "server": ("testserver", 80),
    }
    sent: list[Message] = []

    async def receive() -> Message:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: Message) -> None:
        sent.append(message)

    asyncio.run(_app(4)(scope, receive, send))

    assert sent[0]["status"] == 400
    assert json.loads(sent[1]["body"])["error"] == "invalid_content_length"


def test_fragmented_body_is_counted_without_content_length() -> None:
    scope: dict[str, Any] = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/mcp",
        "raw_path": b"/mcp",
        "query_string": b"",
        "root_path": "",
        "headers": [],
        "client": ("127.0.0.1", 1234),
        "server": ("testserver", 80),
    }
    incoming: list[Message] = [
        {"type": "http.request", "body": b"12", "more_body": True},
        {"type": "http.request", "body": b"34", "more_body": False},
    ]
    sent: list[Message] = []

    async def receive() -> Message:
        return incoming.pop(0)

    async def send(message: Message) -> None:
        sent.append(message)

    asyncio.run(_app(3)(scope, receive, send))

    assert sent[0]["status"] == 413
    assert json.loads(sent[1]["body"])["max_body_bytes"] == 3
