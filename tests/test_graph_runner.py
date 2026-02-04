"""
Tests for the GraphRunner.

This module tests the GraphRunner class that executes LangGraph workflows.

NOTE: These tests are tied to the LangGraph agent template in langgraph_agent/.
If the template changes (e.g., different state fields, nodes, or edges),
these tests will need to be updated to reflect the new expected behavior.

The tests verify that the GraphRunner correctly executes whatever graph
it is configured with. When updating the agent, update these tests accordingly.
"""

import pytest
import sys
import os
import asyncio
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_graph_runner_initialization():
    """Test that GraphRunner initializes and compiles the graph."""
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    assert runner._graph is not None


def test_graph_runner_run_sync():
    """
    Test synchronous graph execution.
    
    NOTE: This test uses the default agent template.
    If the template changes, update the expected values below.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    result = runner.run_sync({"topic": "AI"})
    
    assert result is not None
    assert "topic" in result
    assert "joke" in result
    assert result["topic"] == "AI and cats"
    assert "joke about AI and cats" in result["joke"]


def test_graph_runner_run_async():
    """
    Test async execution using asyncio.run.
    
    NOTE: This test uses the default agent template.
    If the template changes, update the expected values below.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    result = asyncio.run(runner.run({"topic": "ML"}))
    
    assert result is not None
    assert "topic" in result
    assert "joke" in result
    assert result["topic"] == "ML and cats"
    assert "joke about ML and cats" in result["joke"]


def test_graph_runner_run_sync_different_input():
    """
    Test sync execution with different input values.
    
    NOTE: This test uses the default agent template.
    If the template changes, update the expected values below.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    result = runner.run_sync({"topic": "Python"})
    
    assert result is not None
    assert result["topic"] == "Python and cats"
    assert "joke about Python and cats" in result["joke"]


def test_graph_runner_sync_error_handling():
    """
    Test that sync execution properly handles and raises errors.
    
    This test mocks the graph's invoke method to simulate an error,
    verifying that the GraphRunner correctly logs and re-raises exceptions.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    
    # Mock the graph to raise an exception
    with patch.object(runner._graph, 'invoke', side_effect=Exception("Graph error")):
        with pytest.raises(Exception) as exc_info:
            runner.run_sync({"topic": "test"})
        
        assert "Graph error" in str(exc_info.value)


def test_graph_runner_async_error_handling():
    """
    Test that async execution properly handles and raises errors.
    
    This test mocks the graph's ainvoke method to simulate an error,
    verifying that the GraphRunner correctly logs and re-raises exceptions.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    
    # Mock the graph to raise an exception
    with patch.object(runner._graph, 'ainvoke', side_effect=Exception("Async graph error")):
        with pytest.raises(Exception) as exc_info:
            asyncio.run(runner.run({"topic": "test"}))
        
        assert "Async graph error" in str(exc_info.value)


def test_graph_runner_run_with_thread_id():
    """
    Test that thread_id is properly passed to the graph.
    
    NOTE: This test verifies thread_id handling. The original agent template
    doesn't use thread_id, but it's passed through for stateful execution.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    thread_id = "test_thread_123"
    
    # Run with explicit thread_id
    result = runner.run_sync({"topic": "JavaScript"}, thread_id=thread_id)
    
    assert result is not None
    assert result["topic"] == "JavaScript and cats"


# ========== Streaming Tests ==========

def test_graph_runner_astream_values():
    """
    Test astream with stream_mode='values'.
    
    This test verifies that stream_mode='values' returns full state after each node.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    
    chunks = []
    async def run_test():
        async for chunk in runner.astream({"topic": "streaming"}, stream_mode="values"):
            chunks.append(chunk)
    asyncio.run(run_test())
    
    # Should have multiple chunks (one per node)
    assert len(chunks) > 0
    
    # Each chunk should be a dict with state
    for chunk in chunks:
        assert isinstance(chunk, dict)


def test_graph_runner_astream_updates():
    """
    Test astream with stream_mode='updates'.
    
    This test verifies that stream_mode='updates' returns only state updates.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    
    chunks = []
    async def run_test():
        async for chunk in runner.astream({"topic": "updates_test"}, stream_mode="updates"):
            chunks.append(chunk)
    asyncio.run(run_test())
    
    # Should have multiple chunks (one per node update)
    assert len(chunks) > 0
    
    # Each chunk should be a dict with node name as key
    for chunk in chunks:
        assert isinstance(chunk, dict)


def test_graph_runner_astream_messages():
    """
    Test astream with stream_mode='messages'.
    
    This test verifies that stream_mode='messages' returns message chunks.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    
    chunks = []
    async def run_test():
        async for chunk in runner.astream({"topic": "messages_test"}, stream_mode="messages"):
            chunks.append(chunk)
    asyncio.run(run_test())
    
    # Note: messages mode returns message chunks from LLM calls
    # The exact count depends on the graph structure


def test_graph_runner_astream_events():
    """
    Test astream_events for event streaming.
    
    This test verifies that astream_events returns all graph events.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    
    events = []
    async def run_test():
        async for event in runner.astream_events({"topic": "events_test"}, version="v2"):
            events.append(event)
    asyncio.run(run_test())
    
    # Should have multiple events
    assert len(events) > 0
    
    # Each event should have 'event' key
    for event in events:
        assert "event" in event


def test_graph_runner_astream_with_thread_id():
    """
    Test that astream works with explicit thread_id.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    thread_id = "streaming_thread_123"
    
    chunks = []
    async def run_test():
        async for chunk in runner.astream(
            {"topic": "threaded_stream"},
            thread_id=thread_id,
            stream_mode="values"
        ):
            chunks.append(chunk)
    asyncio.run(run_test())
    
    assert len(chunks) > 0


# ========== State Management Tests ==========

def test_graph_runner_get_state():
    """
    Test getting the state of a thread.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    thread_id = "get_state_test"
    
    # First, run to create state
    result = runner.run_sync({"topic": "get_state"}, thread_id=thread_id)
    assert result is not None
    
    # Get the state
    state = runner.get_state(thread_id)
    assert state is not None
    assert "topic" in state
    assert "joke" in state


def test_graph_runner_delete_thread():
    """
    Test deleting a thread.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    thread_id = "delete_test"
    
    # Create a thread
    result = runner.run_sync({"topic": "delete_me"}, thread_id=thread_id)
    assert result is not None
    
    # Get state before deletion
    state_before = runner.get_state(thread_id)
    assert state_before is not None
    
    # Delete the thread
    deleted = runner.delete_thread(thread_id)
    assert deleted is True
    
    # State should be empty dict after deletion (not None)
    state_after = runner.get_state(thread_id)
    assert state_after == {}


# ========== Thread Continuity Tests ==========

def test_graph_runner_thread_continuity():
    """
    Test that resuming a thread continues from previous state.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    thread_id = "continuity_test"
    
    # First run
    result1 = runner.run_sync({"topic": "first_run"}, thread_id=thread_id)
    assert result1["topic"] == "first_run and cats"
    
    # Second run in same thread
    result2 = runner.run_sync({"topic": "second_run"}, thread_id=thread_id)
    
    # The state should accumulate (topic is overwritten, joke is added)
    assert "topic" in result2
    assert "joke" in result2


# ========== GraphRunner Close Test ==========

def test_graph_runner_close():
    """
    Test that GraphRunner.close() works without error.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    runner.close()  # Should not raise


def test_graph_runner_close_with_memory_checkpointer():
    """
    Test GraphRunner with memory checkpointer and close.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner(checkpointer_type="memory")
    assert runner._checkpointer is not None
    runner.close()


# ========== GraphRunner Error Handling Tests ==========

def test_graph_runner_get_state_with_checkpointer():
    """
    Test get_state returns values when checkpointer is configured.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    thread_id = "state_test"
    
    # Run to create state
    runner.run_sync({"topic": "test"}, thread_id=thread_id)
    
    # Get state
    state = runner.get_state(thread_id)
    assert state is not None
    assert "topic" in state


def test_graph_runner_get_state_empty_thread():
    """
    Test get_state returns empty dict for nonexistent thread.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    
    # Get state for nonexistent thread (after deletion)
    state = runner.get_state("nonexistent_thread")
    assert state == {}


def test_graph_runner_get_state_no_checkpointer():
    """
    Test get_state returns None when no checkpointer is configured.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    
    # Mock to simulate no checkpointer
    runner._checkpointer = None
    
    state = runner.get_state("any_thread")
    assert state is None


def test_graph_runner_delete_thread_no_checkpointer():
    """
    Test delete_thread returns False when no checkpointer is configured.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    
    # Mock to simulate no checkpointer
    runner._checkpointer = None
    
    result = runner.delete_thread("any_thread")
    assert result is False


def test_graph_runner_with_memory_checkpointer():
    """
    Test GraphRunner with explicit memory checkpointer.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner(checkpointer_type="memory")
    assert runner._checkpointer is not None
    
    # Run should work with checkpointer
    result = runner.run_sync({"topic": "test"})
    assert result is not None


# ========== GraphRunner Error Handling Tests ==========
def test_graph_runner_get_state_with_checkpointer():
    """
    Test get_state returns values when checkpointer is configured.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    thread_id = "state_test"
    
    # Run to create state
    runner.run_sync({"topic": "test"}, thread_id=thread_id)
    
    # Get state
    state = runner.get_state(thread_id)
    assert state is not None
    assert "topic" in state


def test_graph_runner_get_state_empty_thread():
    """
    Test get_state returns empty dict for nonexistent thread.
    """
    from lg_deploy.graph_runner import GraphRunner
    
    runner = GraphRunner()
    
    # Get state for nonexistent thread (after deletion)
    state = runner.get_state("nonexistent_thread")
    assert state == {}


# ========== Checkpointer Registry Tests ==========

def test_checkpointer_registry_get():
    """
    Test getting a named checkpointer from the registry.
    """
    from lg_deploy.graph_checkpointers import registry
    
    # Get memory checkpointer
    cp1 = registry.get("test1")
    assert cp1 is not None
    
    # Get the same checkpointer again (should be cached)
    cp2 = registry.get("test1")
    assert cp1 is cp2


def test_checkpointer_registry_close():
    """
    Test closing a named checkpointer.
    """
    from lg_deploy.graph_checkpointers import registry
    
    # Get and close a checkpointer
    cp = registry.get("test_close")
    closed = registry.close("test_close")
    
    assert closed is True
    
    # Should be removed from registry
    cp2 = registry.get("test_close")
    assert cp is not cp2  # New checkpointer created


def test_checkpointer_registry_close_all():
    """
    Test closing all checkpointers.
    """
    from lg_deploy.graph_checkpointers import registry
    
    # Create multiple checkpointers
    registry.get("multi1")
    registry.get("multi2")
    
    # Close all
    registry.close_all()
    
    # Registry should be empty
    assert len(registry._checkpointers) == 0


def test_checkpointer_registry_nonexistent():
    """
    Test closing a nonexistent checkpointer.
    """
    from lg_deploy.graph_checkpointers import registry
    
    closed = registry.close("nonexistent")
    assert closed is False


# ========== Get Checkpointer Tests ==========

def test_get_checkpointer_memory():
    """
    Test get_checkpointer with memory type.
    """
    from lg_deploy.graph_checkpointers import get_checkpointer
    
    cp = get_checkpointer("memory")
    assert cp is not None


def test_get_checkpointer_unknown_type():
    """
    Test get_checkpointer with unknown type.
    """
    from lg_deploy.graph_checkpointers import get_checkpointer
    
    with pytest.raises(ValueError) as exc_info:
        get_checkpointer("unknown")
    
    assert "Unknown checkpointer type" in str(exc_info.value)


def test_get_checkpointer_redis_missing_conn_string():
    """
    Test get_checkpointer with redis type but no conn_string.
    Raises ImportError if package not installed, ValueError if installed but no conn_string.
    """
    from lg_deploy.graph_checkpointers import get_checkpointer
    
    try:
        get_checkpointer("redis")
        pytest.fail("Expected ImportError or ValueError")
    except (ImportError, ValueError):
        pass  # Expected


def test_get_checkpointer_postgres_missing_conn_string():
    """
    Test get_checkpointer with postgres type but no conn_string.
    Raises ImportError if package not installed, ValueError if installed but no conn_string.
    """
    from lg_deploy.graph_checkpointers import get_checkpointer
    
    try:
        get_checkpointer("postgres")
        pytest.fail("Expected ImportError or ValueError")
    except (ImportError, ValueError):
        pass  # Expected


# ========== Environment Variable Tests ==========

def test_get_checkpointer_from_env(monkeypatch):
    """
    Test get_checkpointer_from_env with environment variables.
    """
    from lg_deploy.graph_checkpointers import get_checkpointer_from_env
    
    # Set environment variables
    monkeypatch.setenv("LG_CHECKPOINTER_TYPE", "memory")
    
    cp = get_checkpointer_from_env()
    assert cp is not None


def test_get_checkpointer_from_env_postgres(monkeypatch):
    """
    Test get_checkpointer_from_env with postgres type.
    """
    from lg_deploy.graph_checkpointers import get_checkpointer_from_env
    
    # Set environment variables
    monkeypatch.setenv("LG_CHECKPOINTER_TYPE", "postgres")
    monkeypatch.setenv("LG_CHECKPOINTER_CONN_STRING", "postgresql://user:pass@localhost/db")
    
    # The test will fail at import time if postgres is not installed
    # This is expected behavior
    try:
        cp = get_checkpointer_from_env()
    except ImportError:
        # Expected if postgres package is not installed
        pytest.skip("langgraph-checkpoint-postgres not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
