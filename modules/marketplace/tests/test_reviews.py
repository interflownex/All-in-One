from platform_test_support import client_for


def test_public_reviews():
    client = client_for("marketplace")
    response = client.get("/valley/reviews?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "reviews" in data
    assert "total" in data
    assert isinstance(data["reviews"], list)
