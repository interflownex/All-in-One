#!/usr/bin/env python3
"""Entrega web ou aplicativo pronto via Telegram, depois dos gates de verificacao."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import uuid
from pathlib import Path
from urllib import error, parse, request

from scripts.secure_http import require_https_url

TELEGRAM_HOSTS = {"api.telegram.org"}


def env(name: str) -> str | None:
    value = os.environ.get(name)
    return value.strip() if value and value.strip() else None


def telegram_request(method: str, token: str, data: bytes, content_type: str) -> None:
    safe_url = require_https_url(
        f"https://api.telegram.org/bot{token}/{method}",
        allowed_hosts=TELEGRAM_HOSTS,
    )
    req = request.Request(
        safe_url,
        data=data,
        headers={"Content-Type": content_type},
        method="POST",
    )
    try:
        # O endpoint foi validado por HTTPS, porta padrão e allowlist de host.
        with request.urlopen(req, timeout=60) as response:  # nosec B310
            payload = json.loads(response.read().decode("utf-8"))
            if response.status not in range(200, 300) or payload.get("ok") is not True:
                raise RuntimeError("Telegram recusou a entrega.")
    except error.HTTPError as exc:
        raise RuntimeError(f"Telegram retornou HTTP {exc.code} {exc.reason}.") from exc
    except (error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Falha de comunicacao com o Telegram: {exc}.") from exc


def send_web(token: str, chat_id: str, url: str, version: str) -> None:
    message = f"Ambiente web do All-in-One pronto.\nVersao: {version}\nAcesso: {url}"
    data = parse.urlencode({"chat_id": chat_id, "text": message}).encode()
    telegram_request("sendMessage", token, data, "application/x-www-form-urlencoded")


def verify_web_identity(url: str, expected_marker: str) -> None:
    safe_url = require_https_url(url)
    try:
        req = request.Request(
            safe_url, headers={"User-Agent": "all-in-one-release-verifier/1"}
        )
        # A URL pública foi validada como HTTPS, porta padrão e sem credenciais.
        with request.urlopen(req, timeout=30) as response:  # nosec B310
            body = response.read().decode("utf-8", errors="replace")
            if response.status not in range(200, 300):
                raise RuntimeError(f"Ambiente web retornou HTTP {response.status}.")
    except (error.HTTPError, error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Ambiente web nao esta acessivel: {exc}.") from exc
    if expected_marker.casefold() not in body.casefold():
        raise RuntimeError(
            f"Identidade web invalida: marcador esperado ausente ({expected_marker})."
        )


def send_app(token: str, chat_id: str, artifact: Path, version: str) -> None:
    boundary = f"codex-{uuid.uuid4().hex}"
    mime_type = mimetypes.guess_type(artifact.name)[0] or "application/octet-stream"
    fields = {
        "chat_id": chat_id,
        "caption": f"Aplicativo Valley pronto. Versao: {version}",
    }
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                value.encode(),
                b"\r\n",
            ]
        )
    chunks.extend(
        [
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="document"; filename="{artifact.name}"\r\n'.encode(),
            f"Content-Type: {mime_type}\r\n\r\n".encode(),
            artifact.read_bytes(),
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    telegram_request(
        "sendDocument",
        token,
        b"".join(chunks),
        f"multipart/form-data; boundary={boundary}",
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=("web", "app"), required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--url")
    parser.add_argument("--artifact")
    parser.add_argument(
        "--expected-marker", default="<title>All-in-One — Ecossistema Digital</title>"
    )
    parser.add_argument("--verified", action="store_true")
    parser.add_argument("--telegram-token", default=env("TELEGRAM_BOT_TOKEN"))
    parser.add_argument("--telegram-chat-id", default=env("TELEGRAM_CHAT_ID"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if not args.verified:
        print(
            "Entrega recusada: confirme os gates de prontidao com --verified.",
            file=sys.stderr,
        )
        return 2
    if not args.telegram_token or not args.telegram_chat_id:
        print(
            "Telegram exige TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID fora do Git.",
            file=sys.stderr,
        )
        return 2
    if args.kind == "web":
        if not args.url or not args.url.startswith("https://"):
            print("Entrega web exige --url HTTPS publica.", file=sys.stderr)
            return 2
        try:
            verify_web_identity(args.url, args.expected_marker)
        except (RuntimeError, ValueError) as exc:
            print(f"Entrega web recusada: {exc}", file=sys.stderr)
            return 2
        try:
            send_web(args.telegram_token, args.telegram_chat_id, args.url, args.version)
        except (RuntimeError, ValueError) as exc:
            print(f"Entrega web falhou: {exc}", file=sys.stderr)
            return 1
    else:
        if not args.artifact:
            print("Entrega do aplicativo exige --artifact.", file=sys.stderr)
            return 2
        artifact = Path(args.artifact).expanduser().resolve()
        if not artifact.is_file() or artifact.suffix.casefold() != ".apk":
            print(f"APK instalavel nao encontrado: {artifact}", file=sys.stderr)
            return 2
        try:
            send_app(args.telegram_token, args.telegram_chat_id, artifact, args.version)
        except (RuntimeError, ValueError) as exc:
            print(f"Entrega do aplicativo falhou: {exc}", file=sys.stderr)
            return 1
    print(f"Entrega {args.kind} confirmada pelo Telegram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
