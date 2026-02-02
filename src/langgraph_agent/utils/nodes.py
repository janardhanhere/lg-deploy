"""
Node functions for LangGraph agent.

This module defines the node functions that transform the state.
Each node receives the current state and returns updates to be merged
into the state.
"""

from .state import State


def refine_topic(state: State) -> dict:
    """
    Refine the input topic.

    This node demonstrates a simple state transformation that
    modifies the topic field.

    Args:
        state: The current state containing the topic.

    Returns:
        A dictionary of state updates to merge.
    """
    return {"topic": state["topic"] + " and cats"}


def generate_joke(state: State) -> dict:
    """
    Generate a joke based on the topic.

    This node demonstrates generating output based on the state.
    In a real agent, this would call an LLM.

    Args:
        state: The current state containing the refined topic.

    Returns:
        A dictionary containing the generated joke.
    """
    return {"joke": f"This is a joke about {state['topic']}"}
