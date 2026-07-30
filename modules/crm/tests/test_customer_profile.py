from uuid import uuid4
from platform_test_support import client_for

def test_customer_ticket_profile():
    client = client_for("crm")
    user_id = str(uuid4())
    headers = {"X-Actor-User-Id": user_id}
    
    response = client.get(f"/valley/crm/customer-profiles/{user_id}/tickets", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_user_id"] == user_id
    assert "tickets" in data
    assert "reviews" in data
