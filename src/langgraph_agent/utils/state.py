"""
State definitions for LangGraph agent.

This module defines the TypedDict-based state schema used by the LangGraph agent.
The state is pure domain state - it does NOT include deployment concerns like
execution_id, which are managed separately by the deployment layer.
"""

from typing import TypedDict


class State(TypedDict):
    """
    Base state for the LangGraph agent.

    This state contains only domain-specific data. Deployment concerns like
    execution_id, thread_id, and status are managed by the lg-deploy worker.

    Attributes:
        topic: The input topic to process.
        joke: The generated joke output.
    """
    topic: str
    joke: str
