import base64
from io import BytesIO
import os
from uuid import UUID, uuid4

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi.testclient import TestClient
from pypdf import PdfWriter
import psycopg
import pytest

from modules.shared.runtime import create_module_app


POSTGRES_DSN = os.getenv("ALL_IN_ONE_JOBS_POSTGRES_TEST_DSN")
pytestmark = pytest.mark.skipif(not POSTGRES_DSN, reason="DSN PostgreSQL de integracao nao configurado.")


def seed_user(connection, user_id: UUID, nonce: str) -> None:
    connection.execute(
        """INSERT INTO identity.users
           (id, full_name, cpf_document, birth_date, email, phone_e164, password_hash,
            face_hash, liveness_score, terms_accepted_at, lgpd_consent_at, status)
           VALUES (%s, %s, %s, DATE '1990-01-01', %s, %s, %s, %s, 0.9900, NOW(), NOW(), 'active')""",
        (
            user_id,
            f"Usuario {nonce}",
            f"CPF-{nonce}",
            f"{nonce}@example.test",
            f"+55119{str(int(nonce[:7], 16)).zfill(8)[-8:]}",
            f"hash-{nonce}",
            f"face-{nonce}",
        ),
    )


def headers(user_id: UUID, business_id: UUID | None = None, scope: str | None = None) -> dict[str, str]:
    result = {"X-Actor-User-Id": str(user_id)}
    if business_id:
        result.update(
            {
                "X-Business-Id": str(business_id),
                "X-Business-Status": "active",
                "X-Actor-Roles": "recruiter",
                "X-Actor-Scopes": scope or "jobs:resumes:read",
                "X-MFA-Verified": "true",
            }
        )
    return result


def test_jobs_postgres_typed_store_and_private_ctps(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    candidate_id = uuid4()
    recruiter_id = uuid4()
    business_id = uuid4()
    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, candidate_id, uuid4().hex[:12])
        seed_user(connection, recruiter_id, uuid4().hex[:12])
        connection.execute(
            """INSERT INTO business.companies
               (id, user_id, cnpj, root_cnpj, legal_name, legal_representative_user_id, status, created_by, updated_by)
               VALUES (%s, %s, %s, %s, 'Empresa Jobs', %s, 'active', %s, %s)""",
            (business_id, recruiter_id, "12345678000191", "12345678", recruiter_id, recruiter_id, recruiter_id),
        )
        connection.execute(
            """INSERT INTO business.user_company_memberships
               (user_id, company_id, status, created_by, updated_by)
               VALUES (%s, %s, 'active', %s, %s)""",
            (recruiter_id, business_id, recruiter_id, recruiter_id),
        )

    monkeypatch.setenv("ALL_IN_ONE_JOBS_POSTGRES_DSN", POSTGRES_DSN)
    monkeypatch.setenv("ALL_IN_ONE_PRIVATE_DOCUMENT_DIR", str(tmp_path))
    monkeypatch.setenv(
        "ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY",
        base64.urlsafe_b64encode(AESGCM.generate_key(bit_length=256)).decode("ascii"),
    )
    client = TestClient(create_module_app("jobs"))
    assert client.get("/health").json()["storage"] == "postgres_jobs_typed_store"

    resume = client.post(
        "/resources/resumes",
        headers=headers(candidate_id),
        json={
            "user_id": str(candidate_id),
            "payload": {"headline": "Pessoa candidata", "recruiter_visibility": "business_recruiters"},
        },
    )
    assert resume.status_code == 201
    resume_id = resume.json()["id"]

    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    stream = BytesIO()
    writer.write(stream)
    imported = client.post(
        f"/resumes/{resume_id}/imports/ctps-digital",
        headers={**headers(candidate_id), "Content-Type": "application/pdf"},
        content=stream.getvalue(),
    )
    assert imported.status_code == 201

    posting = client.post(
        "/resources/job_postings",
        headers=headers(recruiter_id, business_id, "jobs:manage"),
        json={
            "user_id": str(recruiter_id),
            "payload": {
                "company_id": str(business_id),
                "company_status": "active",
                "title": "Vaga PostgreSQL",
                "description": "Selecao auditada.",
            },
        },
    )
    assert posting.status_code == 201
    published = client.post(
        f"/resources/job_postings/{posting.json()['id']}/actions/publish",
        headers=headers(recruiter_id, business_id, "jobs:manage"),
        json={"reason": "publicacao autorizada"},
    )
    assert published.status_code == 200
    viewed = client.get(
        f"/recruiting/resumes/{resume_id}",
        headers=headers(recruiter_id, business_id),
        params={"purpose": "triagem documentada"},
    )
    assert viewed.status_code == 200

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert connection.execute("SELECT COUNT(*) FROM jobs.resumes WHERE id = %s", (resume_id,)).fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM jobs.resume_documents WHERE resume_id = %s", (resume_id,)).fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM jobs.resume_access_logs WHERE resume_id = %s", (resume_id,)).fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM audit.logs WHERE module = 'jobs'").fetchone()[0] >= 4
        assert connection.execute("SELECT COUNT(*) FROM audit.domain_events WHERE routing_key LIKE 'jobs.%'").fetchone()[0] >= 4
