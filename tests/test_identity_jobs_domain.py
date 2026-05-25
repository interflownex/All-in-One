import base64
from io import BytesIO
from uuid import uuid4

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi.testclient import TestClient
from pypdf import PdfWriter
import pytest

from modules.shared.ctps_import import parse_employment_text
from modules.shared.runtime import create_module_app
from platform_test_support import client_for


def owner_headers(user_id: str) -> dict[str, str]:
    return {"X-Actor-User-Id": user_id}


def recruiter_headers(user_id: str, business_id: str, scope: str = "jobs:resumes:read") -> dict[str, str]:
    return {
        "X-Actor-User-Id": user_id,
        "X-Actor-Roles": "recruiter",
        "X-Actor-Scopes": scope,
        "X-Business-Id": business_id,
        "X-Business-Status": "active",
    }


def test_identity_public_registration_preserves_duplicate_controls() -> None:
    client = client_for("identity")
    nonce = uuid4().hex
    phone_suffix = str(int(nonce[:8], 16)).zfill(10)[-10:]
    payload = {
        "full_name": "Usuario Final Jobs",
        "cpf_document": f"CPF-{nonce[:12]}",
        "email": f"{nonce}@example.test",
        "phone_e164": f"+55{phone_suffix}",
        "face_hash": f"face-{nonce}",
        "terms_accepted_at": "2026-05-25T10:00:00Z",
        "lgpd_consent_at": "2026-05-25T10:00:00Z",
    }

    created = client.post("/registrations", json=payload)
    duplicate = client.post("/registrations", json=payload)

    assert created.status_code == 201
    assert created.json()["status"] == "pending_validation"
    assert duplicate.status_code == 409


def test_ctps_text_extraction_marks_document_import_without_external_claim() -> None:
    records = parse_employment_text(
        """
        Contrato de Trabalho
        Empregador: Empresa Formal LTDA
        CNPJ: 12.345.678/0001-90
        Cargo: Analista
        Inicio: 01/02/2021 Termino: 10/03/2024
        """
    )

    assert len(records) == 1
    assert records[0]["evidence_status"] == "validated_by_document_import"
    assert records[0]["official_verification_status"] == "not_verified_externally"
    assert records[0]["user_activity_description"] is None


def test_jobs_curriculum_provenance_recruiter_gate_and_ctps_document() -> None:
    client = client_for("jobs")
    owner_id = str(uuid4())
    resume = client.post(
        "/resources/resumes",
        headers=owner_headers(owner_id),
        json={
            "user_id": owner_id,
            "payload": {"headline": "Operador logistico", "recruiter_visibility": "business_recruiters"},
        },
    )
    assert resume.status_code == 201
    resume_id = resume.json()["id"]

    informal = client.post(
        "/resources/employment_records",
        headers=owner_headers(owner_id),
        json={
            "user_id": owner_id,
            "payload": {
                "resume_id": resume_id,
                "source_type": "user_declared",
                "employer_name": "Atividade autonoma",
                "started_on": "2022-01-01",
                "is_informal_activity": True,
                "user_activity_description": "Executou entregas autonomas e atendimento.",
            },
        },
    )
    assert informal.status_code == 201
    assert informal.json()["payload"]["evidence_status"] == "self_declared_unverified"

    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    stream = BytesIO()
    writer.write(stream)
    imported = client.post(
        f"/resumes/{resume_id}/imports/ctps-digital",
        headers={**owner_headers(owner_id), "Content-Type": "application/pdf"},
        content=stream.getvalue(),
    )
    assert imported.status_code == 201
    assert imported.json()["document"]["payload"]["evidence_status"] == "validated_by_document_import"
    assert imported.json()["official_verification_status"] == "not_verified_externally"

    denied = client.get(
        f"/recruiting/resumes/{resume_id}",
        headers=owner_headers(str(uuid4())),
        params={"purpose": "selecao"},
    )
    assert denied.status_code == 403

    recruiter_id = str(uuid4())
    business_id = str(uuid4())
    allowed = client.get(
        f"/recruiting/resumes/{resume_id}",
        headers=recruiter_headers(recruiter_id, business_id),
        params={"purpose": "triagem para vaga publicada"},
    )
    assert allowed.status_code == 200
    grouped = allowed.json()["employment_records"]
    assert len(grouped["self_declared_unverified"]) == 1
    assert grouped["validated_by_document_import"] == []


def test_jobs_active_business_can_publish_vacancy_for_candidates() -> None:
    client = client_for("jobs")
    recruiter_id = str(uuid4())
    business_id = str(uuid4())
    headers = {
        **recruiter_headers(recruiter_id, business_id, "jobs:manage"),
        "X-MFA-Verified": "true",
    }
    created = client.post(
        "/resources/job_postings",
        headers=headers,
        json={
            "user_id": recruiter_id,
            "payload": {
                "company_id": business_id,
                "company_status": "active",
                "title": "Analista de Operacoes",
                "description": "Atuar com processos e indicadores.",
            },
        },
    )
    assert created.status_code == 201
    posted = client.post(
        f"/resources/job_postings/{created.json()['id']}/actions/publish",
        headers=headers,
        json={"reason": "vaga autorizada para publicacao"},
    )
    assert posted.status_code == 200
    assert posted.json()["status"] == "published"

    vacancies = client.get("/vacancies", params={"q": "operacoes"})
    assert vacancies.status_code == 200
    assert any(row["id"] == created.json()["id"] for row in vacancies.json())

    candidate_id = str(uuid4())
    resume = client.post(
        "/resources/resumes",
        headers=owner_headers(candidate_id),
        json={
            "user_id": candidate_id,
            "payload": {"headline": "Candidato", "recruiter_visibility": "business_recruiters"},
        },
    )
    application = client.post(
        "/resources/applications",
        headers=owner_headers(candidate_id),
        json={
            "user_id": candidate_id,
            "payload": {"resume_id": resume.json()["id"], "job_posting_id": created.json()["id"]},
        },
    )
    assert application.status_code == 201
    assert application.json()["status"] == "submitted"


def test_jobs_ctps_pdf_is_encrypted_and_downloadable_only_by_owner(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    key = base64.urlsafe_b64encode(AESGCM.generate_key(bit_length=256)).decode("ascii")
    monkeypatch.setenv("ALL_IN_ONE_PRIVATE_DOCUMENT_DIR", str(tmp_path))
    monkeypatch.setenv("ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY", key)
    client = TestClient(create_module_app("jobs"))
    owner_id = str(uuid4())
    resume = client.post(
        "/resources/resumes",
        headers=owner_headers(owner_id),
        json={
            "user_id": owner_id,
            "payload": {"headline": "Candidato protegido", "recruiter_visibility": "business_recruiters"},
        },
    )
    resume_id = resume.json()["id"]
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    stream = BytesIO()
    writer.write(stream)
    original = stream.getvalue()

    imported = client.post(
        f"/resumes/{resume_id}/imports/ctps-digital",
        headers={**owner_headers(owner_id), "Content-Type": "application/pdf"},
        content=original,
    )
    document_id = imported.json()["document"]["id"]
    assert "storage_key" not in imported.json()["document"]["payload"]
    ciphertext = next(tmp_path.rglob("*.aesgcm")).read_bytes()
    assert ciphertext != original
    assert b"%PDF" not in ciphertext

    owner_download = client.get(
        f"/resumes/{resume_id}/documents/{document_id}/content",
        headers=owner_headers(owner_id),
    )
    assert owner_download.status_code == 200
    assert owner_download.content == original

    denied = client.get(
        f"/resumes/{resume_id}/documents/{document_id}/content",
        headers=recruiter_headers(str(uuid4()), str(uuid4())),
    )
    assert denied.status_code == 403


def test_jobs_requires_document_secret_in_production(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("ALL_IN_ONE_ENV", "production")
    monkeypatch.setenv("ALL_IN_ONE_PRIVATE_DOCUMENT_DIR", str(tmp_path))
    monkeypatch.delenv("ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY", raising=False)

    with pytest.raises(RuntimeError, match="obrigatoria em producao"):
        create_module_app("jobs")
