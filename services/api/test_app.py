from fastapi.testclient import TestClient
import app
def test_health():
 r=TestClient(app.app).get("/health"); assert r.status_code==200

def test_metrics():
    client = TestClient(app.app)

    client.get("/health")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "# HELP http_requests_total" in response.text
