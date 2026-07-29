from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from modules.valley_consumer.main import app

client = TestClient(app)
SANDBOX = {"X-Innovation-Sandbox": "true"}


def execute(idea_id: int, payload: dict, action: str = "create"):
    return client.post(
        f"/innovation/round-005/{idea_id}/execute",
        headers=SANDBOX,
        json={"owner_id": str(uuid4()), "action": action, "payload": payload},
    )


def test_catalog_has_all_24_ideas_and_flags_off():
    response = client.get("/innovation/round-005")
    assert response.status_code == 200
    body = response.json()
    assert body["approved"] == 24
    assert len(body["ideas"]) == 24
    assert body["feature_flags_enabled"] == []
    assert body["ideas"][0]["code"] == "VLY-20260728-01"
    assert body["ideas"][-1]["code"] == "VLY-20260728-24"


def test_write_is_blocked_without_flag_or_sandbox():
    response = client.post(
        "/innovation/round-005/1/execute",
        json={"owner_id": str(uuid4()), "action": "create", "payload": {"guardian_ids": ["a", "b"], "quorum": 2}},
    )
    assert response.status_code == 409


def test_every_idea_accepts_a_valid_sandbox_contract():
    future = (datetime.now(UTC) + timedelta(days=5)).isoformat()
    now = datetime.now(UTC).isoformat()
    samples = {
        1: {"guardian_ids": ["g1", "g2"], "quorum": 2},
        2: {"statement": "Responder em até um dia", "metric": "hours", "valid_until": future},
        3: {"starts_at": now, "ends_at": future},
        4: {"total_brl": "10.00", "beneficiaries": [{"amount_brl": "10.00"}]},
        5: {"criteria": ["local"], "offers": [{"id": "a", "local": 1}, {"id": "b", "local": 0}]},
        6: {"owned_model": "A", "candidate_model": "B", "rules": [{"required": True, "matched": True}]},
        7: {"steps": [{"name": "coleta"}, {"name": "entrega"}]},
        8: {"name": "Ponto A", "services": ["water"], "latitude": -19.9, "longitude": -44.1},
        9: {"evidence": ["photo://1"], "category": "it", "opinions": []},
        10: {"stop_id": "stop-1", "vehicle_id": "bus-1", "accessibility_mode": "haptic"},
        11: {"context": "Projeto", "decision": "Escolha", "learning": "Aprendizado"},
        12: {"scenario": "Desconto", "assumptions": ["volume estável"]},
        13: {"item": "água", "minimum_quantity": "2", "current_quantity": "1"},
        14: {"routes": [{"id": "a", "noise": 1}, {"id": "b", "noise": 2}], "impact_weights": {"noise": 1}},
        15: {"incident": "Atraso", "facts": ["prazo vencido"], "proposed_remedies": ["reembolso"]},
        16: {"process_type": "purchase", "preserved_fields": ["receipt"], "retention_reason": "fiscal"},
        17: {"document_id": "doc-1", "purpose": "cadastro", "hidden_fields": ["income"], "expires_at": future},
        18: {"employee_id": str(uuid4()), "hours": "2", "learning_goal": "curso"},
        19: {"professional_id": str(uuid4()), "data_types": ["heart_rate"], "starts_at": now, "ends_at": future},
        20: {"purposes": [{"id": "core", "required": True, "accepted": True}, {"id": "ads", "required": False, "accepted": False}]},
        21: {"property_id": str(uuid4()), "area": "salão", "starts_at": now, "ends_at": future},
        22: {"kind": "time_saved", "amount": "30", "unit": "minutes", "methodology": "comparação de rota"},
        23: {"memory_type": "goal", "content": "meta", "confirmed_at": now},
        24: {"scopes": ["read"], "outbound_fields": ["id"], "inbound_fields": ["status"], "retention_days": 1, "synthetic_only": True},
    }
    for idea_id, payload in samples.items():
        response = execute(idea_id, payload)
        assert response.status_code == 201, (idea_id, response.text)
        assert response.json()["idea_id"] == idea_id


def test_identity_quorum_is_enforced():
    response = execute(1, {"guardian_ids": ["g1", "g2"], "quorum": 3})
    assert response.status_code == 422


def test_finance_receipt_must_reconcile():
    response = execute(4, {"total_brl": "10.00", "beneficiaries": [{"amount_brl": "9.00"}]})
    assert response.status_code == 422


def test_collaborative_diagnosis_has_three_opinion_limit():
    response = execute(9, {"evidence": ["photo://1"], "category": "it", "opinions": [1, 2, 3, 4]})
    assert response.status_code == 422


def test_sanitized_copy_preserves_original():
    response = execute(17, {"document_id": "doc-1", "purpose": "cadastro", "hidden_fields": ["income"], "expires_at": (datetime.now(UTC) + timedelta(days=1)).isoformat()})
    assert response.status_code == 201
    assert response.json()["result"]["original_untouched"] is True


def test_legal_required_purpose_cannot_be_silently_rejected():
    response = execute(20, {"purposes": [{"id": "core", "required": True, "accepted": False}]})
    assert response.status_code == 422


def test_stale_semantic_memory_requires_confirmation():
    old = (datetime.now(UTC) - timedelta(days=100)).isoformat()
    response = execute(23, {"memory_type": "goal", "content": "meta antiga", "confirmed_at": old, "ttl_days": 30})
    assert response.status_code == 201
    assert response.json()["result"]["requires_confirmation"] is True


def test_api_contract_simulation_refuses_real_data():
    response = execute(24, {"scopes": ["read"], "outbound_fields": ["id"], "inbound_fields": ["status"], "retention_days": 1, "synthetic_only": False})
    assert response.status_code == 422


def test_production_flag_cannot_be_enabled_by_contract_route():
    response = client.put("/innovation/round-005/flags/1", json={"enabled": True, "rollout_stage": "production"})
    assert response.status_code == 409


def test_round_004_remains_available():
    response = client.get("/innovation/round-004")
    assert response.status_code == 200
    assert len(response.json()["ideas"]) == 24
