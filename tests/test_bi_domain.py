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


def test_bi_dataset_dashboard_export_journey() -> None:
    client = client_for("bi")
    actor = str(uuid4())
    nonce = uuid4().hex

    dataset = client.post(
        "/resources/datasets",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "name": f"Receita Consolidada {nonce}",
                "source_module": "finance",
                "source_resource_type": "ledger_entries",
                "refresh_mode": "hourly",
            },
        },
    )
    assert dataset.status_code == 201
    assert dataset.json()["status"] == "draft"

    refreshed = client.post(
        f"/resources/datasets/{dataset.json()['id']}/actions/refresh",
        headers=actor_headers(actor),
        json={"reason": "carga ETL sandbox concluida"},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["status"] == "refreshed"

    denied_dataset_publish = client.post(
        f"/resources/datasets/{dataset.json()['id']}/actions/publish",
        headers=actor_headers(actor),
        json={"reason": "publicacao sem MFA"},
    )
    assert denied_dataset_publish.status_code == 403

    published_dataset = client.post(
        f"/resources/datasets/{dataset.json()['id']}/actions/publish",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "dataset validado para consumo analitico"},
    )
    assert published_dataset.status_code == 200
    assert published_dataset.json()["status"] == "published"

    dashboard = client.post(
        "/resources/dashboards",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "dataset_id": dataset.json()["id"],
                "name": "Receita por modulo",
                "definition": {"metric": "gross_revenue", "period": "monthly"},
                "allowed_roles": ["administrator", "analyst"],
            },
        },
    )
    assert dashboard.status_code == 201
    assert dashboard.json()["status"] == "draft"

    denied_dashboard_publish = client.post(
        f"/resources/dashboards/{dashboard.json()['id']}/actions/publish",
        headers=actor_headers(actor),
        json={"reason": "dashboard sem MFA"},
    )
    assert denied_dashboard_publish.status_code == 403

    published_dashboard = client.post(
        f"/resources/dashboards/{dashboard.json()['id']}/actions/publish",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "politica analitica revisada"},
    )
    assert published_dashboard.status_code == 200
    assert published_dashboard.json()["status"] == "published"

    export = client.post(
        "/resources/exports",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "dashboard_id": dashboard.json()["id"],
                "export_format": "csv",
                "requested_at": "2026-07-15T10:00:00Z",
            },
        },
    )
    assert export.status_code == 201
    assert export.json()["status"] == "requested"

    completed_export = client.post(
        f"/resources/exports/{export.json()['id']}/actions/complete",
        headers=actor_headers(actor),
        json={"reason": "arquivo entregue ao cofre analitico"},
    )
    assert completed_export.status_code == 200
    assert completed_export.json()["status"] == "completed"

    missing_allowed_roles = client.post(
        "/resources/dashboards",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "dataset_id": dataset.json()["id"],
                "name": "Dashboard sem politica",
                "definition": {"metric": "gross_revenue"},
            },
        },
    )
    assert missing_allowed_roles.status_code == 422

    outbox = client.get("/events/outbox", headers=actor_headers(actor, "auditor"))
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {
        "bi.dataset.created",
        "bi.dataset.refreshed",
        "bi.dataset.published",
        "bi.dashboard.created",
        "bi.dashboard.published",
        "bi.export.requested",
        "bi.export.completed",
    } <= routing_keys
