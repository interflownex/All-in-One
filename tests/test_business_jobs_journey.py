from uuid import uuid4

from platform_test_support import fresh_client_for


def owner_headers(user_id: str) -> dict[str, str]:
    return {"X-Actor-User-Id": user_id}


def approver_headers(user_id: str) -> dict[str, str]:
    return {
        "X-Actor-User-Id": user_id,
        "X-Actor-Roles": "owner",
        "X-MFA-Verified": "true",
    }


def recruiter_headers(
    user_id: str, business_id: str, scope: str = "jobs:resumes:read"
) -> dict[str, str]:
    return {
        "X-Actor-User-Id": user_id,
        "X-Actor-Roles": "recruiter",
        "X-Actor-Scopes": scope,
        "X-Business-Id": business_id,
        "X-Business-Status": "active",
        "X-MFA-Verified": "true",
    }


def test_business_jobs_candidate_access_journey() -> None:
    business = fresh_client_for("business")
    jobs = fresh_client_for("jobs")
    nonce = uuid4().hex
    recruiter_id = str(uuid4())

    company = business.post(
        "/resources/companies",
        headers=owner_headers(recruiter_id),
        json={
            "user_id": recruiter_id,
            "payload": {
                "cnpj": f"{int(nonce[:12], 16):014d}"[-14:],
                "root_cnpj": f"{int(nonce[:8], 16):08d}"[-8:],
                "legal_name": f"Empresa Jobs {nonce[:8]}",
                "legal_representative_user_id": recruiter_id,
            },
        },
    )
    assert company.status_code == 201
    company_id = company.json()["id"]
    assert company.json()["status"] == "pending_validation"

    approved_company = business.post(
        f"/resources/companies/{company_id}/actions/approve",
        headers=approver_headers(recruiter_id),
        json={"reason": "KYB aprovado para recrutamento"},
    )
    assert approved_company.status_code == 200
    assert approved_company.json()["status"] == "approved"

    job = jobs.post(
        "/resources/job_postings",
        headers=recruiter_headers(recruiter_id, company_id, "jobs:manage"),
        json={
            "user_id": recruiter_id,
            "payload": {
                "company_id": company_id,
                "company_status": "active",
                "title": "Analista de Operacoes",
                "description": "Atuar com operacao, indicadores e atendimento.",
            },
        },
    )
    assert job.status_code == 201
    job_id = job.json()["id"]

    published = jobs.post(
        f"/resources/job_postings/{job_id}/actions/publish",
        headers=recruiter_headers(recruiter_id, company_id, "jobs:manage"),
        json={"reason": "vaga validada pela empresa aprovada"},
    )
    assert published.status_code == 200
    assert published.json()["status"] == "published"

    vacancies = jobs.get("/vacancies", params={"q": "operacoes"})
    assert vacancies.status_code == 200
    assert any(item["id"] == job_id for item in vacancies.json())

    candidate_id = str(uuid4())
    resume = jobs.post(
        "/resources/resumes",
        headers=owner_headers(candidate_id),
        json={
            "user_id": candidate_id,
            "payload": {
                "headline": "Candidato Operacional",
                "recruiter_visibility": "business_recruiters",
            },
        },
    )
    assert resume.status_code == 201
    resume_id = resume.json()["id"]

    application = jobs.post(
        "/resources/applications",
        headers=owner_headers(candidate_id),
        json={
            "user_id": candidate_id,
            "payload": {"resume_id": resume_id, "job_posting_id": job_id},
        },
    )
    assert application.status_code == 201
    assert application.json()["status"] == "submitted"

    denied = jobs.get(
        f"/recruiting/resumes/{resume_id}",
        headers=owner_headers(str(uuid4())),
        params={"purpose": "triagem"},
    )
    assert denied.status_code == 403

    allowed = jobs.get(
        f"/recruiting/resumes/{resume_id}",
        headers=recruiter_headers(recruiter_id, company_id),
        params={"purpose": "triagem para vaga publicada"},
    )
    assert allowed.status_code == 200
    assert allowed.json()["resume"]["id"] == resume_id
