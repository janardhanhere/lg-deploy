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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
