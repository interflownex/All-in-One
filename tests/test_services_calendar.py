from fastapi.testclient import TestClient

from modules.services.main import app

client = TestClient(app)


def test_get_time_slots():
    response = client.get("/providers/mock-provider/time-slots?date=2026-06-10")
    assert response.status_code == 200
    data = response.json()
    assert data["provider_id"] == "mock-provider"
    assert "available_slots" in data
    assert len(data["available_slots"]) > 0


def test_reserve_slot_success():
    response = client.post(
        "/providers/mock-provider/reserve-slot",
        json={"slot": "09:00", "customer_id": "cust-123"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "reserved"


def test_reserve_slot_conflict():
    response = client.post(
        "/providers/mock-provider/reserve-slot",
        json={"slot": "10:00", "customer_id": "cust-123"},
    )
    assert response.status_code == 409
