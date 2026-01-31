import pytest
import time
from fastapi.testclient import TestClient
from lg_deploy.main import app
from lg_deploy.persistance import ExecutionStatus


def test_enqueue_creates_execution_record():
    """Test that enqueue creates an execution record in persistence."""
    with TestClient(app) as client:
        response = client.post("/enqueue")
        assert response.status_code == 200
        data = response.json()
        assert "execution_id" in data
        execution_id = data["execution_id"]

        # Verify execution exists in persistence
        execution = app.state.persistence.get(execution_id)
        assert execution is not None
        # Status could be QUEUED or RUNNING depending on timing
        assert execution.status in [ExecutionStatus.QUEUED, ExecutionStatus.RUNNING]


def test_get_execution_status():
    """Test that we can retrieve execution status."""
    with TestClient(app) as client:
        # Create an execution
        response = client.post("/enqueue")
        execution_id = response.json()["execution_id"]

        # Get status
        response = client.get(f"/execute/{execution_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["execution_id"] == execution_id
        # Status could be QUEUED, RUNNING, or COMPLETED depending on timing
        assert data["status"] in ["QUEUED", "RUNNING", "COMPLETED"]
        assert "created_at" in data


def test_get_nonexistent_execution():
    """Test that 404 is returned for non-existent execution."""
    with TestClient(app) as client:
        response = client.get("/execute/nonexistent-id")
        assert response.status_code == 404


def test_worker_processes_execution():
    """Test that worker processes executions from queue."""
    with TestClient(app) as client:
        # Create an execution
        response = client.post("/enqueue")
        execution_id = response.json()["execution_id"]

        # Wait for worker to process (simulated work takes 2 seconds)
        time.sleep(3)

        # Check execution is completed
        execution = app.state.persistence.get(execution_id)
        assert execution.status == ExecutionStatus.COMPLETED
        assert execution.result is not None
        assert execution.completed_at is not None
