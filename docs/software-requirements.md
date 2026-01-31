# lg-deploy — Software Requirements Specification (Software SRS)
Authors: janardhanhere ( janardhan.balaji@outlook.com )
Date: 28th December 2025 (Updated: 31st January 2026)

## 1. Introduction

This document specifies the **software-level requirements** for **lg-deploy**.  
It refines the system requirements into concrete, testable software behaviors and contracts.

This document focuses on:
- API behavior
- execution semantics
- persistence guarantees
- error handling expectations

---

## 2. Execution Model

### SR-01: Asynchronous Execution Model
The system must follow an **asynchronous execution model**, where execution is decoupled from HTTP request lifecycles.

- HTTP requests must not block on execution completion.
- Execution must continue even if the client disconnects.

---

### SR-02: Execution Lifecycle States
Each execution must transition through a well-defined set of states:

- `QUEUED`
- `RUNNING`
- `COMPLETED`
- `FAILED`

State transitions must be persisted and observable.

---

## 3. API Requirements

### SR-03: Execution Start API
The system must expose an API endpoint that allows clients to start a new execution.

The API must:
- Accept a request describing the execution input
- Generate a unique execution identifier
- Persist initial execution state
- Return immediately with execution metadata

---

### SR-04: Execution Status API
The system must expose an API endpoint that allows clients to retrieve execution state using an execution identifier.

The API must:
- Return the current execution status
- Return execution output if completed
- Return failure information if execution failed

---

### SR-05: Idempotent Status Queries
Execution status queries must be **idempotent** and safe to retry.

---

## 4. Persistence Requirements

### SR-06: Persistence Abstraction
The system must abstract persistence behind a well-defined interface.

- Application logic must not depend on the underlying persistence implementation.
- Persistence backend must be configurable.

---

### SR-07: In-Memory Persistence
The system must support in-memory persistence for:
- development
- testing
- single-process execution

This persistence mode does not guarantee durability across restarts.

---

### SR-08: Durable Persistence
The system must support a durable persistence backend (e.g., PostgreSQL).

When configured:
- Execution state must survive process restarts.
- Execution state must be queryable after restart.

---

## 5. Queue and Scheduling Requirements

### SR-09: Execution Scheduling
The system must enqueue execution requests for asynchronous processing.

- The queue must store execution identifiers, not execution state.
- Scheduling must be decoupled from HTTP request handling.

---

### SR-10: Backpressure Handling
The system must be capable of applying backpressure by controlling execution scheduling and worker concurrency.

---

## 6. Worker Requirements

### SR-11: Independent Worker Execution
Execution workers must operate independently of HTTP request handlers.

- Workers must load execution state from persistence.
- Workers must update execution state during execution.

---

### SR-12: Failure Handling
If an execution fails:
- The failure must be recorded in execution state.
- Error details must be persisted and retrievable.

---

## 7. Observability Requirements

### SR-13: Execution Identification
Each execution must be traceable via a unique execution identifier.

---

### SR-14: Request Correlation
Each HTTP request must be traceable via a request identifier for logging and debugging purposes.

---

### SR-15: Logging
The system must log:
- execution start
- execution completion
- execution failure
- critical state transitions

---

## 8. Error Handling Requirements

### SR-16: Execution Errors
Execution errors must not crash the HTTP API.

- Errors must be isolated per execution.
- Failed executions must not affect other executions.

---

### SR-17: API Errors
The API must return clear and consistent error responses for:
- invalid requests
- unknown execution identifiers
- internal server errors

---

## 9. Non-Functional Software Constraints

### SR-18: Performance
Execution start APIs must respond within a predictable time window independent of execution duration.

---

### SR-19: Concurrency
The system must support multiple concurrent executions without state corruption.

---

### SR-20: Extensibility
The software must be designed to allow:
- additional execution backends
- distributed workers
- alternate queue implementations

---

## 10. Chat and Conversation Requirements [NEW]

### SR-21: Session Management API
The system must expose an API endpoint for creating and managing conversation sessions.

**Endpoint:** `POST /sessions`
**Request:** None (or optional metadata)
**Response:**
```json
{
  "session_id": "uuid",
  "created_at": "timestamp"
}
```

---

### SR-22: Chat Message API
The system must expose an API endpoint for sending messages within a session.

**Endpoint:** `POST /sessions/{session_id}/messages`
**Request:**
```json
{
  "message": "user message content",
  "stream": true
}
```
**Response:** Execution identifier for tracking

---

### SR-23: Conversation History API
The system must expose an API endpoint for retrieving conversation history.

**Endpoint:** `GET /sessions/{session_id}/messages`
**Response:**
```json
{
  "session_id": "uuid",
  "messages": [
    {"role": "user", "content": "...", "timestamp": "..."},
    {"role": "assistant", "content": "...", "timestamp": "..."}
  ]
}
```

---

### SR-24: Session Listing API
The system must expose an API endpoint for listing user sessions.

**Endpoint:** `GET /sessions`
**Response:** List of sessions with metadata (last activity, message count)

---

### SR-25: Streaming Response API
The system must support streaming graph node updates via Server-Sent Events (SSE).

**Endpoint:** `GET /sessions/{session_id}/stream`
**Format:** SSE with event types:
- `node.start`: Node execution started
- `node.complete`: Node execution completed with state
- `message`: Assistant message chunk
- `complete`: Execution finished
- `error`: Execution failed

---

### SR-26: Session Access Verification
Every session-related API must verify that the requesting client owns the session.

- Unauthorized access must return HTTP 403
- Non-existent sessions must return HTTP 404

---

## 11. Data Model Requirements [NEW]

### SR-27: Session Data Model
The system must persist the following session information:

```
Session:
  - session_id: UUID (primary key)
  - created_at: timestamp
  - updated_at: timestamp
  - metadata: JSON object (optional)
```

---

### SR-28: Message Data Model
The system must persist conversation messages:

```
Message:
  - message_id: UUID
  - session_id: UUID (foreign key)
  - role: enum [user, assistant, system]
  - content: text
  - created_at: timestamp
  - execution_id: UUID (optional, links to graph execution)
```

---

### SR-29: Graph State Persistence
The system must persist graph state per session for resumable conversations:

```
GraphState:
  - session_id: UUID
  - checkpoint: JSON (LangGraph checkpoint data)
  - updated_at: timestamp
```

---

## 12. Worker Backend Requirements [NEW]

### SR-30: Pluggable Worker Interface
The system must define a worker interface that supports multiple implementations.

**Required Methods:**
- `start()`: Initialize worker
- `stop()`: Graceful shutdown
- `enqueue(execution_id)`: Add job to queue
- `get_status(execution_id)`: Query job status

---

### SR-31: AsyncWorker Implementation
The system must provide an AsyncWorker using Python asyncio.

**Characteristics:**
- No external dependencies
- In-memory queue
- Single-process execution
- Suitable for development and testing

---

### SR-32: RQWorker Implementation
The system must provide an RQWorker using Redis Queue.

**Characteristics:**
- Requires Redis server
- Persistent queue across restarts
- Supports distributed workers
- Suitable for production

---

### SR-33: Worker Fallback
If the configured worker backend is unavailable at startup, the system must:

1. Log a warning
2. Fall back to AsyncWorker
3. Continue operation without crashing

---

## 13. Traceability

Each software requirement defined in this document must map to:
- one or more system requirements
- one or more test cases
- one or more architectural components

**Traceability Matrix for New Requirements:**

| Software Req | System Req | Description |
|--------------|------------|-------------|
| SR-21 | FR-10 | Session creation API |
| SR-22 | FR-10, FR-12 | Chat message with state |
| SR-23 | FR-11 | Conversation history |
| SR-24 | FR-13 | Session listing |
| SR-25 | FR-14 | Streaming responses |
| SR-26 | FR-15 | Session access control |
| SR-27-29 | FR-11, NFR-08 | Data models |
| SR-30-33 | FR-16 | Pluggable workers |
