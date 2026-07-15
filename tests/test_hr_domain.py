from __future__ import annotations

from uuid import uuid4

from platform_test_support import client_for


def actor_headers(
    user_id: str,
    roles: str = "administrator",
    *,
    mfa_verified: bool = False,
) -> dict[str, str]:
    return {
        "X-Actor-User-Id": user_id,
        "X-Actor-Roles": roles,
        "X-MFA-Verified": "true" if mfa_verified else "false",
    }


def test_hr_employee_payroll_and_training_journey() -> None:
    client = client_for("hr")
    actor = str(uuid4())
    company_id = str(uuid4())
    nonce = uuid4().hex

    employee = client.post(
        "/resources/employees",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "company_id": company_id,
                "employment_type": "clt",
                "admission_date": "2026-07-15",
                "name": "Colaborador jornada HR",
            },
        },
    )
    assert employee.status_code == 201
    assert employee.json()["status"] == "draft"

    payroll = client.post(
        "/resources/payroll_runs",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "company_id": company_id,
                "period": "2026-07",
                "gross_amount_brl": "4200.00",
                "net_amount_brl": "3780.00",
            },
        },
    )
    assert payroll.status_code == 201
    assert payroll.json()["status"] == "open"

    denied_close = client.post(
        f"/resources/payroll_runs/{payroll.json()['id']}/actions/close",
        headers=actor_headers(actor),
        json={"reason": "fechamento sem MFA"},
    )
    assert denied_close.status_code == 403

    closed = client.post(
        f"/resources/payroll_runs/{payroll.json()['id']}/actions/close",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "folha conferida e fechada"},
    )
    assert closed.status_code == 200
    assert closed.json()["status"] == "closed"

    training = client.post(
        "/resources/courses",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "employee_id": employee.json()["id"],
                "course_code": f"onboarding-{nonce}",
                "title": "Onboarding operacional Valley",
                "due_at": "2026-07-31",
            },
        },
    )
    assert training.status_code == 201
    assert training.json()["status"] == "assigned"

    completed_training = client.post(
        f"/resources/courses/{training.json()['id']}/actions/complete",
        headers=actor_headers(actor),
        json={"reason": "treinamento obrigatorio concluido"},
    )
    assert completed_training.status_code == 200
    assert completed_training.json()["status"] == "completed"

    rejected_negative_payroll = client.post(
        "/resources/payroll_runs",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "company_id": company_id,
                "period": "2026-08",
                "gross_amount_brl": "-1.00",
            },
        },
    )
    assert rejected_negative_payroll.status_code == 422

    outbox = client.get("/events/outbox", headers=actor_headers(actor, "auditor"))
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {
        "hr.employee.created",
        "hr.payroll.opened",
        "hr.payroll.closed",
        "hr.training.assigned",
        "hr.training.completed",
    } <= routing_keys
