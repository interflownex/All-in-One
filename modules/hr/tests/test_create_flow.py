from uuid import uuid4

from platform_test_support import client_for


def test_create_and_approve_flow():
    client = client_for("hr")
    actor = str(uuid4())
    headers = {"X-Actor-User-Id": actor}
    created = client.post("/create", headers=headers, json={"user_id": actor, "payload": {"source": "test"}})
    assert created.status_code == 201
    resource_id = created.json()["id"]
    approved = client.post("/approve", headers=headers, json={"id": resource_id, "reason": "validated in test"})
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
