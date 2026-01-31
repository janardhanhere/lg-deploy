# lg-deploy — High Level Architecture Design (HLD)
Authors: janardhanhere ( janardhan.balaji@outlook.com )
Date: 28th December 2025 (Updated: 31st January 2026)

## 1. Overview

**lg-deploy** is a deployment runtime for executing **LangGraph-based agents** in a production environment. The system is designed to support **long-running, stateful executions** while keeping HTTP request handling **non-blocking** and **stateless**.

The architecture separates **request handling** from **execution**, enabling durability, observability, and future horizontal scalability.

---

## 2. Architectural Goals

* Decouple HTTP request lifecycle from execution lifecycle
* Support long-running and resumable executions
* Persist execution state independently of process lifetime
* Enable pluggable persistence backends (in-memory, PostgreSQL)
* Allow future horizontal scaling with minimal refactoring
* Keep the system framework-light and infrastructure-agnostic

---

## 3. High-Level Architecture

```
Clients (CLI / UI / SDK)
        |
        v
+----------------------+
|   HTTP API (FastAPI) |
|  - Validation        |
|  - Request logging   |
|  - Execution control |
+----------+-----------+
           |
           v
+----------------------+
|   Execution Queue    |
|  (async scheduling) |
+----------+-----------+
           |
           v
+----------------------+
|   Execution Worker   |
|  - Runs LangGraph    |
|  - Updates state     |
+----------+-----------+
           |
           v
+----------------------+
|  Persistence Layer   |
|  - In-memory (dev)   |
|  - PostgreSQL (prod) |
+----------------------+
```

---

## 4. Core Components

### 4.1 HTTP API (Control Plane)

**Responsibilities:**

* Accept and validate client requests
* Create execution records
* Enqueue execution jobs
* Return execution identifiers
* Serve execution status queries

**Non-responsibilities:**

* Must not execute LangGraph workflows
* Must not block on long-running tasks
* Must not store execution state in memory

The HTTP API is intentionally **stateless**.

---

### 4.2 Execution Queue (Scheduling Plane)

**Purpose:**

* Decouple request initiation from execution
* Control execution ordering and concurrency
* Provide backpressure

**Design Notes:**

* Queue stores execution identifiers only
* Initial implementation uses `asyncio.Queue`
* Future implementations may use Redis or external brokers

---

### 4.3 Execution Worker (Execution Plane)

**Responsibilities:**

* Consume execution identifiers from the queue
* Load execution state from persistence
* Execute LangGraph workflows
* Update execution state and results

Workers operate independently of HTTP requests and are designed to be:

* restartable
* replaceable
* horizontally scalable in future versions

---

### 4.4 Persistence Layer (Source of Truth)

**Responsibilities:**

* Persist execution state
* Support state retrieval across requests
* Survive process restarts

**Backends:**

* In-memory store (development/testing)
* PostgreSQL store (production)

All execution state is owned exclusively by the persistence layer.

---

## 5. Execution Lifecycle

### 5.1 Execution Start

1. Client sends `POST /execute`
2. API generates a unique `execution_id`
3. Initial execution state is persisted with status `QUEUED`
4. `execution_id` is enqueued for execution
5. API returns immediately to the client

---

### 5.2 Execution Processing

1. Worker dequeues `execution_id`
2. Execution state is loaded from persistence
3. Status is updated to `RUNNING`
4. LangGraph workflow executes
5. Execution state is updated with progress and output

---

### 5.3 Completion and Failure

* On success, status becomes `COMPLETED`
* On error, status becomes `FAILED` with error details
* Execution results remain queryable after completion

---

## 6. Failure Handling

| Failure Scenario    | System Behavior                      |
| ------------------- | ------------------------------------ |
| Client disconnect   | Execution continues                  |
| HTTP process crash  | Execution state persists             |
| Worker crash        | Execution state remains recoverable  |
| Application restart | Unfinished executions can be resumed |

The system avoids coupling execution correctness to HTTP request success.

---

## 7. Scalability Model

### Phase 1 — Single Process

* In-memory queue
* In-memory or PostgreSQL persistence
* Single worker loop

### Phase 2 — Multi-Worker

* Shared persistence backend
* Multiple worker loops
* Controlled concurrency

### Phase 3 — Distributed

* External queue (Redis / SQS)
* Separate worker processes
* Stateless API instances

---

## 8. Design Constraints

* HTTP requests must complete quickly
* Execution must not depend on client connections
* Persistence must be backend-agnostic
* LangGraph execution must remain isolated from HTTP concerns

---

## 9. Chat System Architecture [NEW]

### 9.1 Overview

The chat system extends the execution model to support conversational interactions with LangGraph agents. Each conversation is a session that maintains state across multiple executions.

### 9.2 Session-Based Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client (UI/CLI)                         │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│  HTTP API (FastAPI)                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ POST /       │  │ POST /       │  │ GET /            │  │
│  │ sessions     │  │ sessions/{id}│  │ sessions/{id}/   │  │
│  │              │  │ /messages    │  │ messages         │  │
│  └──────────────┘  └──────┬───────┘  └──────────────────┘  │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Session Manager                                             │
│  - Create/retrieve sessions                                  │
│  - Load previous graph state                                 │
│  - Persist conversation history                              │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│  Execution Queue                    Persistence Layer       │
│  ┌─────────────────┐               ┌──────────────────┐    │
│  │ Async Queue     │               │ Sessions Table   │    │
│  │ or RQ Queue     │               │ Messages Table   │    │
│  └────────┬────────┘               │ Graph State      │    │
└───────────┼────────────────────────└──────────────────┘─────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│  Worker                                                      │
│  - Load session state                                        │
│  - Execute LangGraph with context                            │
│  - Stream updates via SSE                                    │
│  - Save checkpoint                                           │
└─────────────────────────────────────────────────────────────┘
```

### 9.3 Session Lifecycle

**Turn 1 - New Session:**
1. Client `POST /sessions` → Creates session
2. Client `POST /sessions/{id}/messages` → Sends first message
3. Worker loads default/empty graph state
4. LangGraph executes with HumanMessage
5. AIMessage saved to conversation history
6. Graph checkpoint saved for session

**Turn N - Existing Session:**
1. Client `POST /sessions/{id}/messages` → Sends follow-up
2. Worker loads previous graph checkpoint
3. New HumanMessage appended to state
4. LangGraph resumes from checkpoint
5. Updated conversation saved
6. New checkpoint saved

### 9.4 Streaming Architecture

**Server-Sent Events (SSE) Flow:**
```
Client                    Server
  │     GET /stream         │
  │ ──────────────────────> │
  │                         │
  │  <── event: node.start  │
  │  <── data: {"node": "..."}
  │                         │
  │  <── event: node.output │
  │  <── data: {"state": {...}}
  │                         │
  │  <── event: complete    │
  │  <── data: {"final": ...}
```

Event types:
- `node.start`: Node execution begins
- `node.output`: Node produces output
- `message`: AI message chunk (for streaming LLMs)
- `error`: Execution failed
- `complete`: Execution finished

---

## 10. Pluggable Worker Architecture [NEW]

### 10.1 Worker Interface

All worker implementations must conform to:

```python
class BaseWorker(ABC):
    @abstractmethod
    async def start(self): pass
    
    @abstractmethod
    async def stop(self): pass
    
    @abstractmethod
    async def enqueue(self, execution_id: str): pass
    
    @abstractmethod
    def get_status(self, execution_id: str) -> ExecutionStatus: pass
```

### 10.2 AsyncWorker (Default)

**Characteristics:**
- Uses `asyncio.Queue` for in-memory scheduling
- Single-process execution
- No external dependencies
- Suitable for: Development, testing, simple deployments

**Trade-offs:**
- Queue lost on restart
- No horizontal scaling
- Simplest configuration

### 10.3 RQWorker (Production)

**Characteristics:**
- Uses Redis Queue for distributed scheduling
- Persistent queue across restarts
- Supports multiple worker processes
- Suitable for: Production, horizontal scaling

**Components:**
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   API       │────▶│    Redis    │◀────│  Worker 1   │
│  (Enqueue)  │     │   (Queue)   │     │             │
└─────────────┘     └─────────────┘     ├─────────────┤
                                         │  Worker 2   │
                                         │             │
                                         └─────────────┘
```

**Trade-offs:**
- Requires Redis server
- More complex deployment
- Production-grade features

### 10.4 Worker Selection Strategy

Configuration-driven selection:

```python
# config.yaml
worker:
  backend: "rq"  # or "async"
  fallback: true  # fallback to async if rq unavailable
  
  rq:
    redis_url: "redis://localhost:6379"
    queue_name: "lg-deploy"
```

---

## 11. Updated Scalability Model

### Phase 1 — Single Process (Current)

* AsyncWorker with in-memory queue
* In-memory or PostgreSQL persistence
* Single worker loop

### Phase 2 — Multi-Worker with RQ

* RQWorker with Redis queue
* Multiple worker processes
* Shared PostgreSQL persistence
* Horizontal scaling within single host

### Phase 3 — Distributed

* Multiple API instances (stateless)
* Redis queue with multiple workers
* Database persistence cluster
* Load balancer for API

---

## 12. Out of Scope (Current)

* Authentication and authorization
* Multi-tenancy
* Streaming execution output via SSE (planned)
* UI dashboards
* Billing and quotas
* Celery support (RQ preferred)

---

## 13. Summary

The lg-deploy architecture emphasizes **durable execution**, **clear separation of concerns**, and **future scalability**, while remaining minimal and easy to reason about in early versions.
