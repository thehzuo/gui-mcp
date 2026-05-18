# Agent Loom MVP

Agent Loom is a local web control surface for long-horizon agentic execution. This implementation follows the MVP design spec at:

`/Users/hzuo/Downloads/agent_loom_mvp_design_doc.md`

The durable core is:

- Task Contract
- State Ledger
- Autonomy Policy
- Verifier Interface
- Model Capability Registry
- Human Review Gates
- Execution Dashboard

## Project Structure

```text
backend/   FastAPI, SQLAlchemy, SQLite, scheduler, policy, verifiers
frontend/  Vite, React, TypeScript, Tailwind, React Flow
gui-mcp/   Existing scaffold left untouched
```

## Backend

Use Python 3.11:

```bash
cd /Users/hzuo/src/agent-loom/backend
/opt/homebrew/bin/python3.11 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend creates `agent_loom.db` automatically on startup.

Run tests:

```bash
cd /Users/hzuo/src/agent-loom/backend
/opt/homebrew/bin/python3.11 -m pytest
```

Run the full MVP verification suite:

```bash
cd /Users/hzuo/src/agent-loom
bash scripts/test_all.sh
```

This runs backend API/policy/scheduler/persistence tests, frontend render tests, and the frontend production build.

## Frontend

```bash
cd /Users/hzuo/src/agent-loom/frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Demo Flow

1. Create a run.
2. Save the Task Contract.
3. Generate a template DAG.
4. Validate and approve the plan.
5. Start execution from the dashboard.
6. Approve the task-level review gate.
7. Watch the dashboard update through SSE and inspect the ledger timeline.

## Local Command Execution

The MVP includes a trusted local `CommandExecutor`. A task can set:

```json
{
  "executor_type": "command",
  "tool_refs": ["command_executor"],
  "executor_config_json": {
    "command": "printf loom",
    "cwd": "/Users/hzuo/src/agent-loom"
  }
}
```

Command output, stderr, exit code, and duration are recorded in `TaskExecution`.
