# lg-deploy — Software Requirements Specification (Software SRS)
Authors: janardhanhere ( janardhan.balaji@outlook.com )
Date: 28th December 2025

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

## 10. Traceability

Each software requirement defined in this document must map to:
- one or more system requirements
- one or more test cases
- one or more architectural components
