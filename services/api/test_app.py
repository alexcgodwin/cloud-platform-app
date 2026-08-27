from fastapi.testclient import TestClient
import app
def test_health():
 r=TestClient(app.app).get("/health"); assert r.status_code==200
