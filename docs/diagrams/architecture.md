# Architecture Diagram

## Mermaid Source Code

```mermaid
flowchart TB
    %% Clients
    subgraph Clients
        direction LR
        CLI["CLI"]
        React["React Frontend"]
        Streamlit["Python Frontend"]
        SDK["Python SDK"]
    end

    %% API
    subgraph API["Deployment API"]
        REST["REST / HTTP"]
        SSE["SSE Stream<br/>(Graph Events & Tokens)"]
    end

    %% Control Plane
    subgraph ControlPlane
        DeployMgr["Deployment Manager"]
        Monitor["Monitoring"]
    end

    %% Runtime Spine
    subgraph Runtime["Execution Runtime"]
        Scheduler["Scheduler"]
        Workers["Long-running Workers"]
        LangGraphRT["LangGraph Runtime"]
    end

    %% Persistence
    DB[("State / Checkpoints DB")]

    %% Main control flow (vertical spine)
    Clients --> REST
    REST --> DeployMgr
    DeployMgr --> Scheduler
    Scheduler --> Workers
    Workers --> LangGraphRT

    %% Side channels
    LangGraphRT --> DB
    LangGraphRT --> Monitor
    LangGraphRT --> SSE
    SSE --> Clients
```

## Related Documentation

- [High Level Design (HLD)](../architecture-hld.md)
- [Low Level Design (LLD)](../architecture-lld.md)
- [Software Requirements](../software-requirements.md)
- [System Requirements](../system-requirements.md)
- [Test Strategy](../test-strategy.md)

## Files

| File | Description |
|------|-------------|
| `lg-deploy.mmd` | Mermaid source code (version-controlled source of truth) |
