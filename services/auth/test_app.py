from fastapi.testclient import TestClient
import app
def test_health(): assert TestClient(app.app).get("/health").status_code==200
