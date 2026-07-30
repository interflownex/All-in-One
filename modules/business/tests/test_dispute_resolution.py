from uuid import uuid4

from platform_test_support import client_for


def test_resolve_dispute_not_found():
    client = client_for("business")
    actor = str(uuid4())
    dispute_id = str(uuid4())
    headers = {"X-Actor-User-Id": actor, "X-Actor-Company-Id": str(uuid4())}

    # Resolving a non-existent dispute should return 404
    response = client.post(
        f"/valley/disputes/{dispute_id}/resolve",
        headers=headers,
        json={"resolution_notes": "We are resolving this.", "action": "resolve"},
    )
    assert response.status_code == 404
