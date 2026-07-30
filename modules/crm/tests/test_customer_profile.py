from uuid import uuid4

from platform_test_support import client_for


def test_customer_ticket_profile():
    client = client_for("crm")
    user_id = str(uuid4())
    headers = {"X-Actor-User-Id": user_id}

    response = client.get(
        f"/valley/crm/customer-profiles/{user_id}/tickets", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["customer_user_id"] == user_id
    assert "tickets" in data
    assert "reviews" in data


def test_customer_ticket_profile_rejects_another_user():
    client = client_for("crm")
    actor = str(uuid4())
    other_user = str(uuid4())

    response = client.get(
        f"/valley/crm/customer-profiles/{other_user}/tickets",
        headers={"X-Actor-User-Id": actor},
    )

    assert response.status_code == 403
