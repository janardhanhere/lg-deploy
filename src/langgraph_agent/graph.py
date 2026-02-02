"""
Graph definition for the LangGraph agent.

This module contains the graph construction logic including nodes
and edges. It creates the workflow without checkpointer concerns.
"""

from langgraph.graph import StateGraph, START, END

from langgraph_agent.utils.state import State
from langgraph_agent.utils.nodes import refine_topic, generate_joke


def build_graph() -> StateGraph:
    """
    Build the StateGraph with nodes and edges.

    Returns:
        StateGraph builder ready to be compiled.
    """
    builder = StateGraph(State)

    # Add nodes
    builder.add_node("refine_topic", refine_topic)
    builder.add_node("generate_joke", generate_joke)

    # Set up edges
    builder.add_edge(START, "refine_topic")
    builder.add_edge("refine_topic", "generate_joke")
    builder.add_edge("generate_joke", END)

    return builder


def create_graph() -> StateGraph:
    """
    Factory function to create a StateGraph.

    Returns:
        StateGraph builder instance.
    """
    return build_graph()
