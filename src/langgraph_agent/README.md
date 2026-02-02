# LangGraph Agent

This package contains a standalone LangGraph agent definition.

## Requirements

- **Python**: >= 3.11
- **LangGraph**: >= 1.0.7 (see `pyproject.toml` for exact version)

## File Structure

```
langgraph_agent/
├── graph.py              # Graph construction (nodes, edges)
├── cli.py                # CLI tool for testing
├── utils/
│   ├── __init__.py
│   ├── state.py          # State TypedDict definition
│   ├── nodes.py          # Node functions
│   └── tools.py          # Tool integrations
└── tests/
    └── README.md
```

## CLI Testing Tool

Test your graph from the command line:

```bash
# Invoke with input
python -m langgraph_agent.cli topic=AI

# Stream mode
python -m langgraph_agent.cli topic=AI stream

# Multiple inputs
python -m langgraph_agent.cli topic=cats joke=funny
```

## Usage

```python
from langgraph_agent.graph import create_graph

graph = create_graph()
result = await graph.ainvoke({"topic": "AI"})
```

## Customization Guide

### 1. Update State (utils/state.py)

Add or modify fields in the State TypedDict:

```python
class State(TypedDict):
    topic: str
    joke: str
    new_field: str  # Add your custom fields here
```

### 2. Update Nodes (utils/nodes.py)

Modify the node functions to transform your state. **Do not delete or rename the functions** - just update their implementation:

```python
def refine_topic(state: State) -> dict:
    # Update this function to modify your state
    return {"topic": state["topic"] + " and cats"}

def generate_joke(state: State) -> dict:
    # Update this function to generate your output
    return {"joke": f"This is a joke about {state['topic']}"}
```

### 3. Update Graph (graph.py)

The graph structure is predefined. To add new nodes, add them to the `build_graph()` function:

```python
def build_graph() -> StateGraph:
    builder = StateGraph(State)
    
    # Existing nodes
    builder.add_node("refine_topic", refine_topic)
    builder.add_node("generate_joke", generate_joke)
    
    # Add your custom node
    builder.add_node("my_custom_node", my_custom_function)
    
    # Update edges
    builder.add_edge(START, "refine_topic")
    builder.add_edge("refine_topic", "generate_joke")
    # Add your custom edges
    builder.add_edge("generate_joke", "my_custom_node")
    builder.add_edge("my_custom_node", END)
    
    return builder
```

**Important:** Do not delete or rename the existing functions. Just update their implementation or add new functions alongside them.

## File Descriptions

| File | Purpose |
|------|---------|
| `graph.py` | Builds the StateGraph with nodes and edges |
| `cli.py` | CLI tool for testing the graph |
| `utils/state.py` | Defines the State TypedDict |
| `utils/nodes.py` | Contains node functions that transform state |
| `utils/tools.py` | Integration with external tools |
