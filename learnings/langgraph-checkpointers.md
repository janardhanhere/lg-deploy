# LangGraph Memory: Full Working Guide (Sessions, Switching, Persistence)

This document explains and implements how LangGraph memory works when:
- You move between chat sessions
- You leave and later return to a session
- You want persistence across restarts

Everything is based on `thread_id`.

---

## 1. Core Concept

LangGraph does NOT have chats.
It has **THREADS**.

A thread is identified by a `thread_id`.

- Same `thread_id` → resume the same conversation
- Different `thread_id` → start a new conversation

Memory is saved and restored using a **CHECKPOINTER**.

---

## 2. State Definition

This is the shared state for the graph. At minimum, it must include `messages`.

```python
from typing import TypedDict, List
from langchain_core.messages import BaseMessage

class ChatState(TypedDict):
    messages: List[BaseMessage]
```

---

## 3. Basic Node (LLM Call)

```python
from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant")

def chat_node(state: ChatState):
    response = llm.invoke(state["messages"])
    return {
        "messages": state["messages"] + [response]
    }
```

---

## 4. Build the Graph

```python
from langgraph.graph import StateGraph, END

builder = StateGraph(ChatState)

builder.add_node("chat", chat_node)
builder.set_entry_point("chat")
builder.add_edge("chat", END)
```

---

## 5. Development Memory (In-Memory)

⚠️ ONLY for local testing. Memory is lost on restart.

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

graph = builder.compile(checkpointer=checkpointer)
```

---

## 6. Production Memory (Postgres)

✅ Use this for real apps.

```python
from langgraph.checkpoint.postgres import PostgresSaver

POSTGRES_URI = "postgresql://user:password@localhost:5432/langgraph"

with PostgresSaver.from_conn_string(POSTGRES_URI) as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)
```

---

## 7. Start a New Chat Session

Create a unique `thread_id`. You control this (UUID, DB ID, frontend ID, etc).

```python
from langchain_core.messages import HumanMessage

thread_id = "chat_1"

result = graph.invoke(
    {"messages": [HumanMessage(content="Hi, my name is Jana")]},
    {"configurable": {"thread_id": thread_id}}
)

print(result["messages"][-1].content)
```

This conversation is now saved under `chat_1`.

---

## 8. Switch to Another Chat Session

```python
thread_id = "chat_2"

result = graph.invoke(
    {"messages": [HumanMessage(content="What is LangGraph?")]},
    {"configurable": {"thread_id": thread_id}}
)
```

Now you have **TWO** separate conversations:
- `chat_1`
- `chat_2`

They do not share memory.

---

## 9. Return to a Previous Session

Reuse the original `thread_id`.

```python
thread_id = "chat_1"

result = graph.invoke(
    {"messages": [HumanMessage(content="Do you remember my name?")]},
    {"configurable": {"thread_id": thread_id}}
)

print(result["messages"][-1].content)
```

LangGraph will:
1. Load saved state for `chat_1`
2. Append the new message
3. Continue the conversation

---

## 10. How This Works Internally

For each `thread_id`, LangGraph stores:
- Full message history
- State fields
- Node outputs
- Execution metadata

**State is saved after EACH graph step.**

---

## 11. Reset or Delete a Session

**Option A: Delete the thread (recommended)**
```python
checkpointer.delete_thread("chat_1")
```

**Option B: Just stop using the ID**
Create a new `thread_id` instead.

---

## 12. Mapping to a Real App

| App Concept | LangGraph Concept |
|-------------|-------------------|
| Chat tab | `thread_id` |
| New chat | new `thread_id` |
| Switch chats | reuse `thread_id` |
| Delete chat | delete `thread` |

LangGraph does NOT manage this for you.

---

## 13. What Thread Memory Does NOT Do

Thread memory:
- ❌ Does not persist across different `thread_id`s
- ❌ Does not store user facts globally
- ❌ Does not merge chats

If you want: "Remember my name across ALL chats"
You must use **LONG-TERM MEMORY (store)**.

---

## 14. Mental Model (Important)

| Concept | Description |
|---------|-------------|
| **Threads** | Conversations |
| **Checkpointers** | Save conversations |
| **thread_id** | Conversation key |

**Same key** → resume
**New key** → fresh start

---

## 15. When to Use What

| Use Case | Checkpointer |
|----------|--------------|
| Single-session chat | Memory checkpointer |
| Multi-chat UI | Memory checkpointer + ID management |
| User personalization | Add long-term memory store |
| Production app | **Persistent checkpointer REQUIRED** |

---

## Checkpointer Types Summary

| Type | Use Case | Persistence |
|------|----------|-------------|
| `MemorySaver` | Development/Testing | Lost on restart |
| `PostgresSaver` | Production | Persistent |
| `SqliteSaver` | Lightweight production | Persistent |
| `RedisSaver` | High-performance | Persistent |

---

## Best Practices

1. **Always use a checkpointer** - Even for development
2. **Use unique thread_ids** - Generate them systematically
3. **Delete old threads** - Clean up unused sessions
4. **Use persistent checkpointers in production** - Never use `MemorySaver`
5. **Separate concerns** - Thread memory vs. long-term memory
