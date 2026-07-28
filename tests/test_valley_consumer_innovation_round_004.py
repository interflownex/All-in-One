from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from modules.valley_consumer.main import app

client = TestClient(app)


def test_round_decisions_and_p0() -> None:
    response = client.get("/innovation/round-004")
    assert response.status_code == 200
    body = response.json()
    assert len(body["ideas"]) == 24
    assert body["approved"] == 23
    assert body["rejected"] == 1
    assert body["p0"] == [5]
    assert body["ideas"][5]["target_module"] == "marketplace"
    assert body["ideas"][13]["decision"] == "rejected"


def test_rejected_sensorial_custody_cannot_create_record() -> None:
    response = client.post(
        "/innovation/round-004/14/records",
        json={"owner_id": str(uuid4()), "payload": {}},
    )
    assert response.status_code == 409


def test_service_payment_releases_after_deadline_without_client_proof() -> None:
    created = client.post(
        "/innovation/round-004/services/outcome-contracts",
        json={
            "client_id": str(uuid4()),
            "professional_id": str(uuid4()),
            "service_description": "Reparo de conectividade residencial",
            "expected_result": "Sinal restabelecido e medido",
            "amount_brl": "150.00",
            "max_validation_hours": 1,
        },
    ).json()
    delivered_at = datetime.now(UTC)
    delivered = client.post(
        f"/innovation/round-004/services/outcome-contracts/{created['id']}/mark-delivered",
        json={
            "actor": "professional",
            "evidence": ["measurement://signal-restored"],
            "evaluated_at": delivered_at.isoformat(),
        },
    )
    assert delivered.status_code == 200
    resolved = client.post(
        f"/innovation/round-004/services/outcome-contracts/{created['id']}/validate",
        json={
            "actor": "system",
            "evidence": [],
            "evaluated_at": (delivered_at + timedelta(hours=2)).isoformat(),
        },
    )
    assert resolved.status_code == 200
    assert resolved.json()["payment_status"] == "released_to_professional"


def test_mobility_coverage_is_partial_without_full_verified_stack() -> None:
    response = client.post(
        "/innovation/round-004/mobility/providers",
        json={
            "provider_name": "Operador piloto",
            "state_code": "MG",
            "cities": ["Betim"],
            "transport_modes": ["bus"],
            "realtime_api_available": True,
            "ticketing_api_available": False,
            "payment_methods": ["qr_code"],
            "production_verified": False,
            "evidence_urls": [],
        },
    )
    assert response.status_code == 201
    assert response.json()["coverage"] == "partial"


def test_jobs_pilot_requires_company_opt_in() -> None:
    response = client.post(
        "/innovation/round-004/jobs/pilot-companies",
        json={
            "company_id": str(uuid4()),
            "opted_in": False,
            "vacancies": [],
            "consent_text_version": "1.0",
        },
    )
    assert response.status_code == 422


def test_shopping_list_suggests_and_marks_purchase() -> None:
    user_id = uuid4()
    created = client.post(
        "/innovation/round-004/shopping-lists",
        json={
            "user_id": str(user_id),
            "items": [
                {"name": "Shampoo", "quantity": "1", "estimated_price_brl": "20.00"},
                {"name": "Condicionador", "quantity": "1", "estimated_price_brl": "25.00"},
            ],
        },
    )
    assert created.status_code == 201
    suggestion = client.post(
        f"/innovation/round-004/shopping-lists/{user_id}/suggest",
        json={"available_balance_brl": "100.00"},
    )
    assert suggestion.json()["should_suggest_review"] is True
    assert suggestion.json()["fits_available_balance"] is True
    confirmed = client.post(
        f"/innovation/round-004/shopping-lists/{user_id}/confirm-purchase",
        json={"purchased_item_names": ["Shampoo"], "transaction_id": "tx-123"},
    )
    assert confirmed.json()["matched_items"] == 1


def test_medication_schedule_requires_verified_prescription() -> None:
    response = client.post(
        "/innovation/round-004/health/medication-plans",
        json={
            "patient_id": str(uuid4()),
            "prescription_id": "rx-123",
            "medication_name": "Medicamento prescrito",
            "interval_hours": 8,
            "duration_days": 2,
            "first_dose_at": datetime.now(UTC).isoformat(),
            "prescribed_by": "Profissional registrado",
            "prescription_verified": True,
        },
    )
    assert response.status_code == 201
    assert len(response.json()["doses"]) == 6


def test_offline_event_is_idempotent() -> None:
    payload = {
        "device_id": "device-123",
        "module": "marketplace",
        "event_type": "marketplace.order.created",
        "idempotency_key": "order-offline-123",
        "payload": {"order_id": "123"},
        "expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        "signature": "signed-event-placeholder",
    }
    first = client.post("/innovation/round-004/offline/events", json=payload)
    second = client.post("/innovation/round-004/offline/events", json=payload)
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert second.json()["deduplicated"] is True
