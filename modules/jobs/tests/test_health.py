from platform_test_support import client_for


def test_health():
    response = client_for("jobs").get("/health")
    assert response.status_code == 200
    assert response.json()["module"] == "jobs"
