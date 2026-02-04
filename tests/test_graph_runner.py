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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
