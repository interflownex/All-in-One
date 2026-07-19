#!/usr/bin/env python3
"""Envia o APK gerado para Telegram e/ou e-mail usando credenciais locais."""

from __future__ import annotations

import argparse
import mimetypes
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path
from urllib import error, request


def env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name, default)
    if value is None:
        return None
    value = value.strip()
    return value or None


def resolve_apk(path_text: str) -> Path:
    apk = Path(path_text).expanduser().resolve()
    if not apk.is_file():
        raise FileNotFoundError(f"APK nao encontrado: {apk}")
    return apk


def send_to_telegram(apk: Path, bot_token: str, chat_id: str, caption: str | None) -> None:
    boundary = "----codex-valley-apk-boundary"
    crlf = "\r\n"
    body: list[bytes] = []

    def add_field(name: str, value: str) -> None:
        body.append(f"--{boundary}{crlf}".encode())
        body.append(f'Content-Disposition: form-data; name="{name}"{crlf}{crlf}'.encode())
        body.append(value.encode())
        body.append(crlf.encode())

    def add_file(name: str, filename: str, data: bytes, mime_type: str) -> None:
        body.append(f"--{boundary}{crlf}".encode())
        body.append(
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"{crlf}'.encode()
        )
        body.append(f"Content-Type: {mime_type}{crlf}{crlf}".encode())
        body.append(data)
        body.append(crlf.encode())

    add_field("chat_id", chat_id)
    if caption:
        add_field("caption", caption)
    mime_type = mimetypes.guess_type(apk.name)[0] or "application/octet-stream"
    add_file("document", apk.name, apk.read_bytes(), mime_type)
    body.append(f"--{boundary}--{crlf}".encode())

    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    req = request.Request(url, data=b"".join(body), method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    try:
        with request.urlopen(req, timeout=60) as response:
            if response.status < 200 or response.status >= 300:
                raise RuntimeError(f"Telegram retornou HTTP {response.status}")
    except error.HTTPError as exc:
        detalhe = ""
        try:
            corpo = exc.read().decode("utf-8", errors="replace").strip()
        except Exception:
            corpo = ""
        if corpo:
            detalhe = f": {corpo}"
        raise RuntimeError(
            f"Falha ao enviar para Telegram: HTTP {exc.code} {exc.reason}{detalhe}"
        ) from exc
    except error.URLError as exc:
        raise RuntimeError(f"Falha ao enviar para Telegram: {exc}") from exc


def send_to_email(
    apk: Path,
    recipient: str,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str | None,
    smtp_password: str | None,
    sender: str,
    use_tls: bool,
    subject: str,
) -> None:
    message = EmailMessage()
    message["To"] = recipient
    message["From"] = sender
    message["Subject"] = subject
    message.set_content("Segue o APK solicitado em anexo.")

    mime_type = mimetypes.guess_type(apk.name)[0] or "application/octet-stream"
    maintype, subtype = mime_type.split("/", 1)
    message.add_attachment(apk.read_bytes(), maintype=maintype, subtype=subtype, filename=apk.name)

    if use_tls:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port, timeout=60) as server:
            server.starttls(context=context)
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(message)
        return

    with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=60) as server:
        if smtp_user and smtp_password:
            server.login(smtp_user, smtp_password)
        server.send_message(message)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", default="apps/valley-android/app/build/outputs/apk/debug/app-debug.apk")
    parser.add_argument("--caption", default="APK Valley Consumer pronto para teste.")
    parser.add_argument("--telegram-token", default=env("TELEGRAM_BOT_TOKEN"))
    parser.add_argument("--telegram-chat-id", default=env("TELEGRAM_CHAT_ID"))
    parser.add_argument("--email-to", default=env("APK_EMAIL_TO"))
    parser.add_argument("--email-from", default=env("APK_EMAIL_FROM"))
    parser.add_argument("--smtp-host", default=env("SMTP_HOST"))
    parser.add_argument("--smtp-port", type=int, default=int(env("SMTP_PORT", "465") or "465"))
    parser.add_argument("--smtp-user", default=env("SMTP_USER"))
    parser.add_argument("--smtp-password", default=env("SMTP_PASSWORD"))
    parser.add_argument("--smtp-tls", action="store_true", default=(env("SMTP_TLS", "false") or "false").lower() == "true")
    parser.add_argument("--subject", default="APK Valley Consumer")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    apk = resolve_apk(args.apk)

    targets: list[str] = []
    if args.telegram_token or args.telegram_chat_id:
        if not args.telegram_token or not args.telegram_chat_id:
            print("Telegram exige TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID.", file=sys.stderr)
            return 2
        send_to_telegram(apk, args.telegram_token, args.telegram_chat_id, args.caption)
        targets.append("telegram")

    if args.email_to:
        if not args.smtp_host:
            print("E-mail exige SMTP_HOST.", file=sys.stderr)
            return 2
        email_from = args.email_from or args.smtp_user or "codex@localhost"
        send_to_email(
            apk=apk,
            recipient=args.email_to,
            smtp_host=args.smtp_host,
            smtp_port=args.smtp_port,
            smtp_user=args.smtp_user,
            smtp_password=args.smtp_password,
            sender=email_from,
            use_tls=args.smtp_tls,
            subject=args.subject,
        )
        targets.append("email")

    if not targets:
        print(
            "Nenhum destino configurado. Defina TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID e/ou APK_EMAIL_TO.",
            file=sys.stderr,
        )
        return 2

    print(f"APK enviado com sucesso para: {', '.join(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
