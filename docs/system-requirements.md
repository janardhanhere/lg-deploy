# lg-deploy — System Requirements Specification (SRS)
Authors: janardhanhere( janardhan.balaji@outlook.com )
Date: 28th December 2025 (Updated: 31st January 2026)

## 1. Purpose

The purpose of **lg-deploy** is to provide a **reliable and scalable runtime** for executing **LangGraph-based agents** in a production environment.

The system enables users to start, monitor, and manage **long-running, stateful agent executions** without coupling the execution lifetime to the lifecycle of HTTP requests.

lg-deploy is designed to act as a backend execution platform that supports durability, observability, and future horizontal scalability.

---

## 2. Scope

lg-deploy is responsible for the following capabilities:

- Accepting execution requests for LangGraph workflows.
- Managing execution lifecycles independently of client connections.
- Supporting long-running executions that may exceed HTTP timeouts.
- Persisting execution state across multiple requests.
- Persisting execution state across process restarts when using a durable backend.
- Allowing clients to query execution status and retrieve execution results.
- Supporting multiple persistence backends, including:
  - In-memory persistence (for development and testing)
  - Database-backed persistence (e.g., PostgreSQL) for production use

lg-deploy is **not responsible** for authoring LangGraph workflows or managing client-side logic.

---

## 3. Actors

### 3.1 Primary Actors

- **Developer**  
  Integrates lg-deploy into applications, services, or platforms.

- **Client Application**  
  A CLI, SDK, or frontend application that starts executions and queries their status.

### 3.2 Secondary Actors

- **Execution Worker**  
  Internal system component responsible for executing LangGraph workflows.

- **Persistence Backend**  
  Storage system responsible for maintaining execution state and results.

---

## 4. Functional Requirements

### FR-01: Start Execution  
The system must allow clients to initiate a new execution by submitting an execution request.

---

### FR-02: Execution Identification  
The system must generate a **globally unique execution identifier** for each execution.

---

### FR-03: Non-Blocking Request Handling  
The system must return control to the client without waiting for the execution to complete.

---

### FR-04: Execution State Persistence  
The system must persist execution state in a way that allows it to be retrieved independently of the request that initiated the execution.

---

### FR-05: Execution Status Query  
The system must allow clients to query the current status of an execution using its execution identifier.

---

### FR-06: Execution Isolation  
The system must ensure that execution state is isolated per execution and does not interfere with other executions.

---

### FR-07: Long-Running Execution Support  
The system must support executions that run for an unbounded duration.

---

### FR-08: Failure Awareness  
The system must detect execution failures and make failure information available to clients.

---

### FR-09: Multiple Persistence Backends  
The system must support multiple persistence backends, including:
- In-memory persistence for development and testing
- Durable database-backed persistence for production environments

---

### FR-10: Session-Based Execution [NEW]  
The system must support **session identifiers** to group related executions into conversations.

---

### FR-11: Conversation History Persistence [NEW]  
The system must persist conversation history (message list) per session for retrieval across multiple requests.

---

### FR-12: Stateful Graph Execution [NEW]  
The system must support resuming graph execution from previous conversation state when a session identifier is provided.

---

### FR-13: Conversation Listing [NEW]  
The system must allow clients to list all conversations for a given session or user.

---

### FR-14: Message Streaming [NEW]  
The system should support streaming graph node updates to clients in real-time.

---

### FR-15: Session Access Control [NEW]  
The system must verify session ownership before allowing access to conversation data.

---

### FR-16: Pluggable Worker Backend [NEW]  
The system must support multiple worker backend implementations including:
- AsyncWorker (default): Uses Python asyncio, zero external dependencies
- RQWorker: Uses RQ (Redis Queue) for distributed execution
If the configured worker backend is unavailable, the system must fall back to the default AsyncWorker.

---

## 5. Non-Functional Requirements

### NFR-01: Reliability  
Execution state must not be lost due to HTTP request termination or client disconnection.

---

### NFR-02: Durability  
When a durable persistence backend is configured, execution state must survive application restarts.

---

### NFR-03: Performance  
Execution initiation requests must complete within a short and predictable time frame.

---

### NFR-04: Scalability  
The system must be designed such that execution throughput can be increased without changing API semantics.

---

### NFR-05: Observability  
The system must provide sufficient logging and identifiers to trace execution lifecycle events.

---

### NFR-06: Extensibility
The system must allow future integration of:
- Additional persistence backends
- Distributed execution workers
- External queueing systems

---

### NFR-07: Security and Isolation [NEW]
The system must ensure conversation data is isolated and protected from unauthorized access.

---

### NFR-08: Conversation Durability [NEW]
When durable persistence is configured, conversation history must survive application restarts.

---

## 6. Constraints

- Execution lifecycle must not depend on client connections.
- Execution state must be managed exclusively by the system.
- Persistence mechanisms must be backend-agnostic from the perspective of the API.

---

## 7. Assumptions

- LangGraph workflows are provided externally and are valid.
- Clients may disconnect, retry, or fail independently of execution progress.
- Execution workloads may vary significantly in duration and complexity.

---

## 8. Out of Scope (Initial Versions)

The following are explicitly out of scope for the initial versions of lg-deploy:

- Authentication and authorization
- Multi-tenant isolation
- User interfaces or dashboards
- Billing, quotas, or rate limiting
- ~~Streaming execution output to clients~~ (Moved to FR-14)

---

## 9. Success Criteria

The system is considered successful if it can:

- Start and manage multiple concurrent executions
- Persist execution state reliably
- Allow clients to observe execution progress and results
- Recover gracefully from failures

---

## 10. Traceability

All architectural decisions, low-level designs, and test cases must trace back to the requirements defined in this document.
