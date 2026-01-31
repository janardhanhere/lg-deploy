from fastapi.testclient import TestClient
from lg_deploy.main import app


def test_enqueue_adds_execution_id():
    """Test that enqueue creates an execution and adds it to the queue for processing."""
    with TestClient(app) as client:
        response = client.post("/enqueue")
        assert response.status_code == 200
        data = response.json()
        assert "execution_id" in data
        execution_id = data["execution_id"]

        # Verify execution was created in persistence
        # (the worker will process it from the queue)
        execution = app.state.persistence.get(execution_id)
        assert execution is not None
        assert execution.execution_id == execution_id
