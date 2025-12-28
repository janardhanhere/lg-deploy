from fastapi.testclient import TestClient
from lg_deploy.main import app


def test_app_lifespan_and_health():
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert app.state.ready is True
