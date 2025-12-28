# lg-deploy — Test Strategy
Authors: janardhanhere ( janardhan.balaji@outlook.com )
Date: 28th December 2025

## 1. Purpose

This document defines the **testing approach and quality strategy** for lg-deploy.

The goal of the test strategy is to ensure that lg-deploy:

* Meets all defined system and software requirements
* Behaves correctly under normal and failure conditions
* Remains reliable as features evolve

This document focuses on **what is tested, how it is tested, and at which level**.

---

## 2. Testing Principles

The following principles guide all testing activities:

* Tests must be **automated by default**
* Tests must be **repeatable and deterministic**
* Business logic must be testable in isolation
* External dependencies must be mockable
* Failures must be observable and debuggable

---

## 3. Test Levels

Testing is divided into multiple levels to ensure correctness at different scopes.

---

### 3.1 Unit Tests

**Purpose:**
Verify individual components in isolation.

**Scope:**

* ExecutionState lifecycle transitions
* ExecutionStore implementations
* ExecutionQueue behavior
* Worker execution logic (mocked dependencies)

**Characteristics:**

* No external services
* Fast execution
* Deterministic results

**Examples:**

* Creating and updating execution state
* Persisting and retrieving execution state from in-memory store
* Valid state transitions

---

### 3.2 Integration Tests

**Purpose:**
Verify interaction between multiple components.

**Scope:**

* HTTP API + persistence layer
* HTTP API + execution queue
* Worker + persistence backend

**Characteristics:**

* Uses real components
* May use test database instances
* Slower than unit tests

**Examples:**

* Starting an execution via API and observing persisted state
* Worker processing queued execution
* Failure handling during execution

---

### 3.3 System Tests

**Purpose:**
Validate end-to-end behavior of the system.

**Scope:**

* Full execution lifecycle
* Long-running execution handling
* Recovery after process restart

**Characteristics:**

* Uses production-like configuration
* May involve multiple workers
* Focuses on correctness over speed

**Examples:**

* Start execution → query status → completion
* Restart system mid-execution and resume

---

## 4. Persistence Testing

### 4.1 In-Memory Persistence Tests

* Verify correct behavior in single-process mode
* Ensure state is correctly stored and retrieved
* Confirm state loss on restart is expected

---

### 4.2 Database Persistence Tests

* Verify durability across restarts
* Validate schema integrity
* Ensure correct state transitions under concurrent access

A dedicated test database must be used.

---

## 5. Failure and Edge Case Testing

The system must be tested against failure scenarios, including:

* Worker crashes during execution
* Invalid execution identifiers
* Execution exceptions
* Queue saturation
* Persistence backend unavailability

Failures must:

* Be isolated per execution
* Be recorded in execution state
* Not crash the system

---

## 6. Observability Testing

Tests must verify:

* Request IDs are generated and propagated
* Execution IDs appear in logs
* Error logs contain sufficient context

---

## 7. Performance and Concurrency Testing

Performance tests must validate:

* Execution start API latency
* Concurrent execution handling
* Queue backpressure behavior

These tests may be executed separately from CI.

---

## 8. Continuous Integration (CI)

CI pipelines must:

* Run unit tests on every pull request
* Run integration tests on main branch
* Generate test coverage reports
* Fail builds on test failures

---

## 9. Test Coverage Expectations

* Core business logic must have high coverage
* Infrastructure and glue code may have lower coverage
* Coverage metrics must not override test quality

---

## 10. Out of Scope

The following are not covered by this test strategy:

* UI testing
* Load testing at internet scale
* Security and penetration testing

---

## 11. Traceability

All tests must trace back to:

* System requirements
* Software requirements
* Architectural components

This ensures full coverage of intended system behavior.
