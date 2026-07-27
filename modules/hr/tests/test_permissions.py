from uuid import uuid4

from platform_test_support import client_for


def test_create_auth_boundary():
    response = client_for("hr").post("/create", json={"user_id": str(uuid4()), "payload": {}})
    assert response.status_code == 401
