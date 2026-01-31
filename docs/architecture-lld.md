# lg-deploy — Low Level Design (LLD)
Authors: janardhanhere ( janardhan.balaji@outlook.com )
Date: 28th December 2025 (Updated: 31st January 2026)

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

## 13. Chat System Data Models [NEW]

### 13.1 Session

Represents a conversation session that groups related executions.

**Fields:**

* `session_id: str`
  Globally unique identifier for the session.

* `created_at: datetime`
  Timestamp when the session was created.

* `updated_at: datetime`
  Timestamp of the last activity in the session.

* `metadata: dict`
  Optional metadata (title, tags, etc.).

---

### 13.2 Message

Represents a single message in a conversation.

**Fields:**

* `message_id: str`
  Globally unique identifier for the message.

* `session_id: str`
  Reference to the parent session.

* `role: MessageRole`
  Type of message sender: `USER`, `ASSISTANT`, or `SYSTEM`.

* `content: str`
  Message content.

* `created_at: datetime`
  Timestamp when the message was created.

* `execution_id: str | None`
  Optional link to the graph execution that produced this message.

---

### 13.3 GraphCheckpoint

Represents a LangGraph checkpoint for session resumption.

**Fields:**

* `session_id: str`
  Reference to the session.

* `checkpoint: dict`
  Serialized LangGraph checkpoint data.

* `updated_at: datetime`
  Timestamp of the last checkpoint update.

---

## 14. Extended Persistence Layer [NEW]

### 14.1 SessionStore Interface

```python
class SessionStore(Protocol):
    def create_session(session: Session) -> None
    def get_session(session_id: str) -> Session | None
    def list_sessions() -> list[Session]
    def update_session(session: Session) -> None
    
    def create_message(message: Message) -> None
    def get_messages(session_id: str) -> list[Message]
    
    def save_checkpoint(checkpoint: GraphCheckpoint) -> None
    def get_checkpoint(session_id: str) -> GraphCheckpoint | None
```

---

## 15. Worker Interface Design [NEW]

### 15.1 BaseWorker (Abstract Interface)

```python
from abc import ABC, abstractmethod

class BaseWorker(ABC):
    @abstractmethod
    async def start(self) -> None:
        """Initialize and start the worker."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Gracefully shutdown the worker."""
        pass
    
    @abstractmethod
    async def enqueue(self, execution_id: str) -> None:
        """Add an execution to the queue."""
        pass
    
    @abstractmethod
    def get_status(self, execution_id: str) -> ExecutionStatus:
        """Get the current status of an execution."""
        pass
```

---

### 15.2 AsyncWorker (Default Implementation)

Uses `asyncio.Queue` for in-memory scheduling.

**Characteristics:**

* Single-process execution
* Queue lost on restart
* No external dependencies

**Implementation Notes:**

```python
class AsyncWorker(BaseWorker):
    def __init__(self, queue: asyncio.Queue, persistence: Persistence):
        self.queue = queue
        self.persistence = persistence
        self._task: asyncio.Task | None = None
    
    async def start(self) -> None:
        self._task = asyncio.create_task(self._run())
    
    async def _run(self) -> None:
        while True:
            execution_id = await self.queue.get()
            await self._process(execution_id)
```

---

### 15.3 RQWorker (Production Implementation)

Uses Redis Queue for distributed execution.

**Characteristics:**

* Requires Redis server
* Persistent queue across restarts
* Supports multiple worker processes

**Implementation Notes:**

```python
from rq import Queue
from redis import Redis

class RQWorker(BaseWorker):
    def __init__(self, redis_url: str, persistence: Persistence):
        self.redis = Redis.from_url(redis_url)
        self.queue = Queue(connection=self.redis)
        self.persistence = persistence
    
    async def start(self) -> None:
        # Start RQ worker process
        pass
    
    async def enqueue(self, execution_id: str) -> None:
        self.queue.enqueue(self._process, execution_id)
```

---

### 15.4 Worker Factory

```python
def create_worker(
    config: WorkerConfig,
    persistence: Persistence
) -> BaseWorker:
    """Factory function for creating appropriate worker."""
    
    if config.backend == "rq":
        try:
            return RQWorker(config.redis_url, persistence)
        except ConnectionError:
            if config.fallback:
                logger.warning("RQ unavailable, falling back to AsyncWorker")
                return AsyncWorker(asyncio.Queue(), persistence)
            raise
    
    return AsyncWorker(asyncio.Queue(), persistence)
```

---

## 16. Chat API Endpoints [NEW]

### 16.1 Session Management

**POST /sessions**
* Creates a new conversation session
* Returns: `{"session_id": "...", "created_at": "..."}`

**GET /sessions**
* Lists all sessions
* Returns: `[{"session_id": "...", "updated_at": "...", "message_count": N}]`

---

### 16.2 Message Handling

**POST /sessions/{session_id}/messages**
* Sends a message in a session
* Request: `{"message": "...", "stream": true}`
* Returns: `{"execution_id": "..."}`

**GET /sessions/{session_id}/messages**
* Retrieves conversation history
* Returns: `{"messages": [{"role": "...", "content": "...", "timestamp": "..."}]}`

---

### 16.3 Streaming Endpoint

**GET /sessions/{session_id}/stream**
* Server-Sent Events endpoint for real-time updates
* Event types: `node.start`, `node.output`, `message`, `error`, `complete`

---

## 17. Database Schema [NEW]

### 17.1 PostgreSQL Schema

```sql
-- Sessions table
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Messages table
CREATE TABLE messages (
    message_id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    role VARCHAR(20) CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    execution_id UUID
);

-- Graph checkpoints table
CREATE TABLE graph_checkpoints (
    session_id UUID PRIMARY KEY REFERENCES sessions(session_id),
    checkpoint JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Executions table (extended)
ALTER TABLE executions ADD COLUMN session_id UUID REFERENCES sessions(session_id);
ALTER TABLE executions ADD COLUMN events JSONB DEFAULT '[]';

-- Indexes
CREATE INDEX idx_messages_session ON messages(session_id, created_at);
CREATE INDEX idx_executions_session ON executions(session_id);
```

---

## 18. Traceability

Each component defined in this document must map directly to:

* System requirements
* Software requirements
* Test cases
* Production behavior

**LLD to SR Mapping:**

| LLD Component | Software Requirement |
|---------------|---------------------|
| Session, Message, GraphCheckpoint | SR-27, SR-28, SR-29 |
| SessionStore | SR-30 |
| BaseWorker, AsyncWorker, RQWorker | SR-31, SR-32, SR-33 |
| Chat API Endpoints | SR-21, SR-22, SR-23, SR-24, SR-25 |
| Database Schema | SR-27, SR-28, SR-29 |
