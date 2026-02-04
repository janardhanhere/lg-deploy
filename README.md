# lg-deploy

Open-source deployment runtime for LangGraph agents, built for scalable and production use.

## Architecture

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

[View detailed diagram](docs/diagrams/architecture.md)

## Documentation

See the [docs](docs/) folder for all documentation.

## Requirements

- Python 3.11.9

## Goals

- Provide a robust and scalable deployment runtime for LangGraph agents.
- Docker deployment support.
- Easy integration with existing LangGraph workflows.
- Plugins to connect to various frontends like react, streamlit etc.
- CLI support for managing deployments.

## Authors

- janardhanhere

## License

- Apache 2.0
