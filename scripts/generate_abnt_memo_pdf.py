#!/usr/bin/env python3
"""Generate a simple ABNT-style PDF from a Markdown-like text file.

This intentionally avoids external dependencies because the workspace runtime
may not have pandoc, wkhtmltopdf, reportlab or pip available.
"""

from __future__ import annotations

import argparse
import textwrap
import zlib
from pathlib import Path

PAGE_W = 595.28
PAGE_H = 841.89
MARGIN_LEFT = 85.04
MARGIN_TOP = 85.04
MARGIN_RIGHT = 56.69
MARGIN_BOTTOM = 56.69
FONT_SIZE = 11
LINE_HEIGHT = 16
TITLE_SIZE = 14
SMALL_SIZE = 9
MAX_CHARS = 88


def pdf_escape(text: str) -> str:
    text = text.encode("cp1252", errors="replace").decode("cp1252")
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def normalize_line(line: str) -> tuple[str, str]:
    stripped = line.strip()
    if not stripped:
        return "blank", ""
    if stripped.startswith("# "):
        return "h1", stripped[2:].strip()
    if stripped.startswith("## "):
        return "h2", stripped[3:].strip()
    if stripped.startswith("### "):
        return "h3", stripped[4:].strip()
    if stripped.startswith("- "):
        return "bullet", stripped[2:].strip()
    if stripped.startswith("|"):
        return "table", stripped
    return "p", stripped


def wrap_text(text: str, width: int = MAX_CHARS) -> list[str]:
    if not text:
        return [""]
    return textwrap.wrap(
        text, width=width, replace_whitespace=False, drop_whitespace=True
    ) or [""]


def iter_render_lines(markdown: str) -> list[tuple[str, str]]:
    rendered: list[tuple[str, str]] = []
    in_table = False
    for raw in markdown.splitlines():
        kind, text = normalize_line(raw)
        if kind == "table":
            if (
                set(text.replace("|", "").replace(":", "").replace("-", "").strip())
                == set()
            ):
                continue
            cells = [cell.strip() for cell in text.strip("|").split("|")]
            text = " | ".join(cells)
            for part in wrap_text(text, 96):
                rendered.append(("table", part))
            in_table = True
            continue
        if in_table and kind != "table":
            rendered.append(("blank", ""))
            in_table = False
        if kind == "blank":
            rendered.append((kind, text))
        elif kind == "bullet":
            wrapped = wrap_text("- " + text, 84)
            for index, part in enumerate(wrapped):
                rendered.append(("p", part if index == 0 else "  " + part))
        elif kind in {"h1", "h2", "h3"}:
            rendered.append((kind, text.upper() if kind == "h1" else text))
        else:
            for part in wrap_text(text):
                rendered.append((kind, part))
    return rendered


def build_pages(lines: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
    pages: list[list[tuple[str, str]]] = [[]]
    y = PAGE_H - MARGIN_TOP
    for kind, text in lines:
        extra = 8 if kind in {"h1", "h2"} else 0
        height = LINE_HEIGHT + extra
        if y - height < MARGIN_BOTTOM:
            pages.append([])
            y = PAGE_H - MARGIN_TOP
        pages[-1].append((kind, text))
        y -= height
    return pages


def page_stream(page: list[tuple[str, str]], page_num: int, total: int) -> bytes:
    cmds = ["BT"]
    y = PAGE_H - MARGIN_TOP
    for kind, text in page:
        if kind == "blank":
            y -= LINE_HEIGHT
            continue
        size = FONT_SIZE
        font = "F1"
        if kind == "h1":
            size = TITLE_SIZE
            font = "F2"
            y -= 4
        elif kind in {"h2", "h3"}:
            size = 12
            font = "F2"
            y -= 2
        elif kind == "table":
            size = SMALL_SIZE
            font = "F3"
        cmds.append(f"/{font} {size} Tf")
        cmds.append(f"{MARGIN_LEFT:.2f} {y:.2f} Td ({pdf_escape(text)}) Tj")
        cmds.append(f"{-MARGIN_LEFT:.2f} {-LINE_HEIGHT:.2f} Td")
        y -= LINE_HEIGHT
    footer = f"Pagina {page_num} de {total}"
    cmds.append(
        f"/F1 9 Tf {PAGE_W - MARGIN_RIGHT - 70:.2f} {MARGIN_BOTTOM - 18:.2f} Td ({pdf_escape(footer)}) Tj"
    )
    cmds.append("ET")
    return "\n".join(cmds).encode("cp1252", errors="replace")


def write_pdf(markdown: str, output: Path) -> None:
    pages = build_pages(iter_render_lines(markdown))
    objects: list[bytes] = []

    def add(obj: bytes) -> int:
        objects.append(obj)
        return len(objects)

    catalog_id = add(b"<< /Type /Catalog /Pages 2 0 R >>")
    assert catalog_id == 1
    pages_id = add(b"")
    font1_id = add(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman /Encoding /WinAnsiEncoding >>"
    )
    font2_id = add(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Bold /Encoding /WinAnsiEncoding >>"
    )
    font3_id = add(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>"
    )

    page_ids: list[int] = []
    for idx, page in enumerate(pages, start=1):
        stream = page_stream(page, idx, len(pages))
        compressed = zlib.compress(stream)
        stream_id = add(
            b"<< /Length "
            + str(len(compressed)).encode()
            + b" /Filter /FlateDecode >>\nstream\n"
            + compressed
            + b"\nendstream"
        )
        page_id = add(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W:.2f} {PAGE_H:.2f}] "
            f"/Resources << /Font << /F1 {font1_id} 0 R /F2 {font2_id} 0 R /F3 {font3_id} 0 R >> >> "
            f"/Contents {stream_id} 0 R >>".encode()
        )
        page_ids.append(page_id)

    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects[pages_id - 1] = (
        f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as fh:
        fh.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for obj_id, obj in enumerate(objects, start=1):
            offsets.append(fh.tell())
            fh.write(f"{obj_id} 0 obj\n".encode())
            fh.write(obj)
            fh.write(b"\nendobj\n")
        xref = fh.tell()
        fh.write(f"xref\n0 {len(objects) + 1}\n".encode())
        fh.write(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            fh.write(f"{offset:010d} 00000 n \n".encode())
        fh.write(
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    write_pdf(args.input.read_text(encoding="utf-8"), args.output)


if __name__ == "__main__":
    main()
