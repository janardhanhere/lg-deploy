from fastapi.testclient import TestClient
from lg_deploy.main import app
import asyncio
import pytest


def test_enqueue_adds_execution_id():
    with TestClient(app) as client:
        response = client.post("/enqueue")
        assert response.status_code == 200
        data = response.json()
        assert "execution_id" in data
        execution_id = data["execution_id"]

        # Check that the execution_id is in the queue
        queue = app.state.execution_queue
        # The queue is async, so we need to check its contents
        # Use asyncio loop to get the item (non-blocking)
        loop = asyncio.get_event_loop()
        queued_id = loop.run_until_complete(queue.get())
        assert queued_id == execution_id
        # Optionally, put it back for other tests
        loop.run_until_complete(queue.put(queued_id))
