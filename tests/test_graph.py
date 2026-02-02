"""
Tests for the LangGraph agent graph.

This module tests that graph.py has the necessary function names.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_graph_has_build_graph_function():
    """Verify graph.py has build_graph function."""
    from langgraph_agent.graph import build_graph
    assert callable(build_graph)


def test_graph_has_create_graph_function():
    """Verify graph.py has create_graph function."""
    from langgraph_agent.graph import create_graph
    assert callable(create_graph)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
