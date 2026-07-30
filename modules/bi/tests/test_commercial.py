from uuid import uuid4
from platform_test_support import client_for

def test_commercial_insights_series():
    client = client_for("bi")
    actor = str(uuid4())
    headers = {"X-Actor-User-Id": actor}
    
    response = client.get("/valley/bi/commercial-insights/series", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "historical_series" in data
    assert isinstance(data["historical_series"], list)
