# LangGraph Streaming Modes

This document provides examples and explanations of different streaming modes available in LangGraph. Use this as a reference when implementing streaming features in the GraphRunner.

---

## Overview of Streaming Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `values` | Stream complete state snapshots after each node | Debugging, full state visibility |
| `updates` | Stream only what changed after each node | Efficient change tracking |
| `messages` | Stream token-by-token LLM output | Chat interfaces, real-time responses |
| `debug` | Stream debug information | Development, troubleshooting |
| `custom` | Stream application-specific events | Progress tracking, custom events |

---

## 1. VALUES Mode - Full State Snapshots

Stream the complete state after each node execution.

```python
def example_values_mode():
    """Stream full state after each node."""
    graph = create_example_graph()
    initial_state = {
        "messages": [],
        "step_count": 0,
        "result": ""
    }

    # Stream with 'values' mode
    for state in graph.stream(initial_state, stream_mode="values"):
        print(f"Step {state['step_count']}:")
        print(f" Messages: {state['messages']}")
        print(f" Result: {state['result']}")
```

**Output:**
```
Step 0:
 Messages: []
 Result:
Step 1:
 Messages: ["Researching topic..."]
 Result:
Step 2:
 Messages: ["Researching topic...", "Analyzing data..."]
 Result:
Step 3:
 Messages: ["Researching topic...", "Analyzing data...", "Creating summary..."]
 Result: Final analysis complete
```

---

## 2. UPDATES Mode - State Changes Only

Stream only the changes (deltas) after each node execution.

```python
def example_updates_mode():
    """Stream only what changed after each node."""
    graph = create_example_graph()
    initial_state = {
        "messages": [],
        "step_count": 0,
        "result": ""
    }

    # Stream with 'updates' mode
    for node_name, updates in graph.stream(initial_state, stream_mode="updates"):
        print(f"Node '{node_name}' updated:")
        print(f" Changes: {updates}")
```

**Output:**
```
Node 'research' updated:
 Changes: {'messages': ['Researching topic...'], 'step_count': 1}
Node 'analyze' updated:
 Changes: {'messages': ['Analyzing data...'], 'step_count': 2}
Node 'summarize' updated:
 Changes: {'messages': ['Creating summary...'], 'step_count': 3, 'result': 'Final analysis complete'}
```

---

## 3. COMBINED Modes - Multiple Modes Simultaneously

Stream multiple modes at the same time.

```python
def example_combined_modes():
    """Use multiple streaming modes simultaneously."""
    graph = create_example_graph()
    initial_state = {
        "messages": [],
        "step_count": 0,
        "result": ""
    }

    # Stream with multiple modes
    for chunk in graph.stream(
        initial_state,
        stream_mode=["updates", "debug"]
    ):
        print(f"Chunk received: {chunk}")
```

---

## 4. MESSAGES Mode - Token-by-Token Streaming

Stream LLM output token-by-token for real-time responses.

```python
async def example_chat_with_streaming():
    """Token-by-token streaming for chat interfaces."""
    graph = create_chat_graph()

    async for event in graph.astream(
        {"query": "Explain quantum computing"},
        stream_mode="messages"
    ):
        # Event contains token-by-token output
        if event['type'] == 'token':
            print(event['content'], end='', flush=True)
        elif event['type'] == 'tool_call':
            print(f"\n[Using tool: {event['tool']}]")
```

**Conceptual Output:**
```
Chat: Hello! Let me help you with that...
(In production, this would stream token-by-token)
```

---

## 5. CUSTOM Mode - Application-Specific Events

Stream custom events for progress tracking or application-specific data.

```python
def example_custom_mode():
    """Custom event streaming for progress tracking."""
    # In practice, your nodes would use StreamWriter to emit events:
    def long_running_node(state: GraphState, writer: StreamWriter):
        for i in range(100):
            # Do some work...
            writer.write({
                'type': 'progress',
                'percentage': i + 1,
                'message': f'Processing item {i+1}/100'
            })
        return state

    for event in graph.stream(initial_state, stream_mode="custom"):
        if event['type'] == 'progress':
            print(f"Progress: {event['percentage']}% - {event['message']}")
```

**Output:**
```
Progress: 25% - Processing data chunk 1/4
Progress: 50% - Processing data chunk 2/4
Progress: 75% - Processing data chunk 3/4
Progress: 100% - Complete!
```

---

## Implementation in GraphRunner

### Adding Streaming to GraphRunner

```python
class GraphRunner:
    def __init__(self):
        self._graph: CompiledStateGraph = create_graph().compile()
    
    async def stream(
        self,
        input_state: Dict[str, Any],
        stream_mode: str = "updates"
    ):
        """
        Stream graph execution with specified mode.
        
        Args:
            input_state: Initial state for the graph.
            stream_mode: One of 'values', 'updates', 'messages', 'debug', 'custom'
        
        Yields:
            Chunks of the stream based on the mode.
        """
        async for chunk in self._graph.astream(input_state, stream_mode=stream_mode):
            yield chunk
    
    async def stream_multi(
        self,
        input_state: Dict[str, Any],
        stream_modes: List[str] = ["updates"]
    ):
        """
        Stream with multiple modes simultaneously.
        
        Args:
            input_state: Initial state for the graph.
            stream_modes: List of modes to stream.
        
        Yields:
            Tuples of (mode, chunk) for each chunk.
        """
        async for chunk in self._graph.astream(input_state, stream_mode=stream_modes):
            yield chunk
```

---

## Quick Reference

| Use Case | Recommended Mode |
|----------|-----------------|
| Debugging state | `values` |
| Efficient updates | `updates` |
| Chatbot responses | `messages` |
| Development | `debug` |
| Progress bars | `custom` |
| Multiple views | `["updates", "messages"]` |

---

## Key Takeaways

1. **Use `values`** for complete state at each step (great for debugging)
2. **Use `updates`** for efficient change tracking (recommended for production)
3. **Use `messages`** for token-by-token LLM output (chat interfaces)
4. **Use `custom`** for application-specific events (progress tracking)
5. **Use `debug`** for development and troubleshooting
6. **Combine modes** with: `stream_mode=['updates', 'messages']`
