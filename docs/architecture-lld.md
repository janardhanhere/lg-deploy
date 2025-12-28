# lg-deploy — Low Level Design (LLD)
Authors: janardhanhere ( janardhan.balaji@outlook.com )
Date: 28th December 2025

## 1. Purpose

This document defines the **low-level software design** for **lg-deploy**.
It specifies concrete data models, interfaces, and component responsibilities derived from the system and software requirements.

This document serves as the **implementation blueprint** for the system.

---

## 2. Core Concepts

### 2.1 Execution

An **Execution** represents a single run of a LangGraph workflow.
Each execution is uniquely identified and progresses through a defined lifecycle.

---

## 3. Data Models

### 3.1 ExecutionState

Represents the persisted state of an execution.

**Fields:**

* `execution_id: str`
  Globally unique identifier for the execution.

* `status: ExecutionStatus`
  Current lifecycle state of the execution.

* `input: dict`
  Input payload used to start the execution.

* `output: dict | None`
  Output produced by the execution, if completed successfully.

* `error: str | None`
  Error message if the execution failed.

* `created_at: datetime`
  Timestamp when the execution was created.

* `updated_at: datetime`
  Timestamp of the last state update.

---

### 3.2 ExecutionStatus

An enumeration defining valid execution lifecycle states.

**Allowed values:**

* `QUEUED`
* `RUNNING`
* `COMPLETED`
* `FAILED`

State transitions must follow a valid lifecycle progression.

---

## 4. Persistence Layer

### 4.1 ExecutionStore Interface

All persistence operations must be accessed through a common abstraction.

```python
class ExecutionStore(Protocol):
    def create(state: ExecutionState) -> None
    def get(execution_id: str) -> ExecutionState | None
    def update(state: ExecutionState) -> None
```

**Responsibilities:**

* Persist execution state
* Retrieve execution state by identifier
* Update execution state atomically

---

### 4.2 InMemoryExecutionStore

**Purpose:**

* Development and testing
* Single-process execution

**Characteristics:**

* Uses in-memory data structures
* No durability guarantees
* Fast access
* State is lost on process restart

---

### 4.3 PostgresExecutionStore

**Purpose:**

* Production-grade persistence
* Durable execution state storage

**Characteristics:**

* Uses PostgreSQL as backing store
* Supports asynchronous operations
* Execution state survives application restarts

---

## 5. Queue and Scheduling

### 5.1 ExecutionQueue

Abstract queue responsible for scheduling execution work.

```python
class ExecutionQueue(Protocol):
    async def enqueue(execution_id: str) -> None
    async def dequeue() -> str
```

**Design Notes:**

* Queue stores **execution identifiers only**
* Execution state is always retrieved from persistence
* Initial implementation uses `asyncio.Queue`
* Future implementations may use Redis or external brokers

---

## 6. Worker Design

### 6.1 ExecutionWorker

Responsible for executing LangGraph workflows.

**Responsibilities:**

* Consume execution identifiers from the queue
* Load execution state from the persistence layer
* Update execution lifecycle states
* Execute LangGraph workflows
* Persist execution results or failure details

**Execution Flow:**

1. Dequeue execution identifier
2. Load execution state
3. Update status to `RUNNING`
4. Execute LangGraph workflow
5. Update status to `COMPLETED` or `FAILED`

---

## 7. HTTP API Layer

### 7.1 Application Factory

The application must be created using a factory function:

```python
def create_app() -> FastAPI
```

This enables:

* Dependency injection
* Environment-specific configuration
* Test isolation

---

### 7.2 Lifespan Management

FastAPI lifespan hooks must be used to:

* Initialize persistence backend
* Initialize execution queue
* Start execution workers
* Gracefully shut down workers on application shutdown

---

### 7.3 Middleware

#### Request Logging Middleware

**Responsibilities:**

* Generate or propagate a request identifier
* Log request start and completion
* Attach request identifier to response headers

---

## 8. Configuration

### 8.1 Configuration Sources

Configuration must be provided via:

* Environment variables
* Configuration files (future extension)

**Examples:**

* Persistence backend type
* Database connection string
* Worker concurrency level

---

## 9. Error Handling

### 9.1 Execution Errors

* Execution errors must be captured and persisted
* Errors must not crash the worker process
* Failed executions must not affect other executions

---

### 9.2 API Errors

* Invalid requests must return client errors
* Unknown execution identifiers must return a not-found error
* Internal failures must return server errors

---

## 10. Concurrency Model

* HTTP handlers are stateless
* Execution workers run independently
* Persistence layer enforces state consistency
* Queue controls execution scheduling and backpressure

---

## 11. Testability Considerations

The design must allow:

* Mocking of the `ExecutionStore`
* Mocking of the `ExecutionQueue`
* Isolated worker testing
* Deterministic execution state transitions

---

## 12. Traceability

Each component defined in this document must map directly to:

* System requirements
* Software requirements
* Test cases
* Production behavior
