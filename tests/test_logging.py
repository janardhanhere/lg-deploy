import logging
from fastapi.testclient import TestClient
from lg_deploy.main import app


def test_request_logging_emits_logs(caplog):
    caplog.set_level(logging.INFO, logger="lg_deploy")

    with TestClient(app) as client:
        response = client.get("/health")

    # Basic request success
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers

    # Extract log messages
    messages = [record.message for record in caplog.records]

    assert "request_started" in messages
    assert "request_completed" in messages
