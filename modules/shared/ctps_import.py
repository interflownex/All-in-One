from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import re
from typing import Any

from pypdf import PdfReader


CPF_PATTERN = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
CNPJ_PATTERN = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
DATE_PATTERN = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")
BLOCK_START = re.compile(r"(?:empregador|contrato\s+de\s+trabalho|vinculo)", re.IGNORECASE)
EMPLOYER_LABEL = re.compile(
    r"(?:empregador|razao\s+social|nome\s+empresarial)\s*:?\s*(.+)", re.IGNORECASE
)
ROLE_LABEL = re.compile(r"(?:ocupacao|cargo|cbo)\s*:?\s*(.+)", re.IGNORECASE)


def _clean_lines(text: str) -> list[str]:
    return [line.strip() for line in text.replace("\r", "\n").split("\n") if line.strip()]


def _value_for(pattern: re.Pattern[str], lines: list[str]) -> str | None:
    for line in lines:
        match = pattern.search(line)
        if match and match.group(1).strip():
            return match.group(1).strip()
    return None


def parse_employment_text(text: str) -> list[dict[str, Any]]:
    """Extract conservative employment blocks without inventing missing CTPS data."""
    lines = _clean_lines(text)
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if BLOCK_START.search(line) and current:
            blocks.append(current)
            current = []
        current.append(line)
    if current:
        blocks.append(current)

    records: list[dict[str, Any]] = []
    for block in blocks:
        material = "\n".join(block)
        cnpj = CNPJ_PATTERN.search(material)
        dates = DATE_PATTERN.findall(material)
        employer_name = _value_for(EMPLOYER_LABEL, block)
        if not employer_name and cnpj:
            employer_name = "Empregador identificado no documento"
        if not employer_name or not dates:
            continue
        records.append(
            {
                "source_type": "ctps_digital_pdf_import",
                "evidence_status": "validated_by_document_import",
                "official_verification_status": "not_verified_externally",
                "employer_name": employer_name,
                "employer_cnpj": cnpj.group(0) if cnpj else None,
                "role_title": _value_for(ROLE_LABEL, block),
                "started_on": dates[0],
                "ended_on": dates[1] if len(dates) > 1 else None,
                "user_activity_description": None,
            }
        )
    return records


def extract_ctps_pdf(contents: bytes) -> dict[str, Any]:
    if not contents.startswith(b"%PDF"):
        raise ValueError("Arquivo enviado nao e PDF.")
    try:
        reader = PdfReader(BytesIO(contents))
        if reader.is_encrypted:
            raise ValueError("PDF protegido por senha nao pode ser importado.")
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("PDF invalido ou ilegivel.") from exc

    cpf_match = CPF_PATTERN.search(text)
    records = parse_employment_text(text)
    return {
        "document_type": "ctps_digital_pdf",
        "sha256": sha256(contents).hexdigest(),
        "page_count": len(reader.pages),
        "cpf_extracted": cpf_match.group(0) if cpf_match else None,
        "evidence_status": "validated_by_document_import",
        "official_verification_status": "not_verified_externally",
        "extraction_status": "records_extracted" if records else "requires_manual_review",
        "employment_records": records,
    }
