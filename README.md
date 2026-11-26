# AgentReliability

A deterministic evaluation harness for measuring whether AI customer support agents actually carry out their claimed actions, rather than relying on LLM self-reporting or LLM-as-a-judge.

---

## Architecture

```mermaid
flowchart TD
    subgraph Task["Benchmark Task"]
        TF["Fixture & Invariants"]
        UM["Customer Message"]
    end

    subgraph Agents["Agent Adapters"]
        PG["Plain Gemini (Zero-Framework)"]
        LG["LangGraph (StateGraph)"]
    end

    subgraph Harness["Deterministic Test Harness"]
        GW["ToolGateway (Camera / TraceRecorder)"]
        ENV["SupportEnvironment (Ground Truth State)"]
        EVAL["Outcome Evaluator (Invariants Referee)"]
    end

    subgraph Storage["Persistence & Reporting"]
        DB[("PostgreSQL")]
        DASH["FastAPI + Single-Page Dashboard"]
    end

    UM --> PG & LG
    PG & LG -->|Tool Calls| GW
    GW -->|Mutations| ENV
    TF --> ENV
    ENV -->|Snapshot| EVAL
    EVAL -->|Pass / Fail / Errors| DB
    GW -->|Traced Events| DB
    DB --> DASH
```

---

## How to Run

### 1. Prerequisites
- Python 3.12+ and [uv](https://github.com/astral-sh/uv)
- Docker Desktop (for PostgreSQL)

### 2. Setup Database & Migrations
```bash
# Start PostgreSQL
docker compose up -d

# Run migrations
uv run alembic upgrade head
```

### 3. Run Automated Tests (Offline)
```bash
uv run pytest
```

### 4. Run Live Benchmark Batch
```bash
uv run python -m agent_reliability.runner --repeats 5
```

### 5. Launch Visual Dashboard
```bash
uv run fastapi dev src/agent_reliability/api.py
```
Open `http://127.0.0.1:8000` to inspect runs, trace events, and evaluator outcomes.

---

## Milestone 1 Benchmark Summary (`batch_20261126_080707`)

- **Model:** `gemini-3.1-flash-lite` (Temperature: 0.0, Step limit: 8)
- **Sample:** 5 repeats $\times$ 3 tasks $\times$ 2 agents = 30 runs (+ 6 controls)
- **Pass Rates:** 
  - `plain_gemini`: 100% (Avg 2.67 tool calls)
  - `langgraph_gemini`: 100% (Avg 2.33 tool calls)
- **Stability Observation:** LangGraph had 100% tool-call consistency (exactly 4 calls on task 1), whereas Plain Gemini experienced a 9-step wobble on repeat #3 before recovering.

> **Disclaimer:** These results reflect a controlled 3-task sandbox with clean, synthetic inputs. They do not claim production readiness or general agent reliability.