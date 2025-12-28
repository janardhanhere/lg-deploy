# lg-deploy — High Level Architecture Design (HLD)
Authors: janardhanhere ( janardhan.balaji@outlook.com )
Date: 28th December 2025

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

## 9. Out of Scope (Initial Versions)

* Authentication and authorization
* Multi-tenancy
* Streaming execution output
* UI dashboards
* Billing and quotas

---

## 10. Summary

The lg-deploy architecture emphasizes **durable execution**, **clear separation of concerns**, and **future scalability**, while remaining minimal and easy to reason about in early versions.
