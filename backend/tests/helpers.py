from __future__ import annotations

from fastapi.testclient import TestClient


def create_run_with_contract(
    client: TestClient,
    *,
    allowed_tools: list[str] | None = None,
    max_autonomy_level: str = "L3",
) -> dict:
    run = client.post("/api/runs", json={"name": "MVP verification", "description": "automated test"}).json()
    response = client.put(
        f"/api/runs/{run['id']}/contract",
        json={
            "goal": "Build a DAG execution flow.",
            "success_criteria": ["Plan executes", "Ledger records mutations"],
            "forbidden_losses": ["No production changes"],
            "allowed_tools": allowed_tools or ["mock_executor", "command_executor", "test_runner"],
            "human_approval_boundaries": ["before_plan_execution", "before_irreversible_action"],
            "risk_class": "MEDIUM",
            "max_autonomy_level": max_autonomy_level,
            "notes": "",
        },
    )
    assert response.status_code == 200
    return run


def generate_and_lock_plan(client: TestClient, run_id: str) -> dict:
    plan = client.post(f"/api/runs/{run_id}/plans/generate").json()
    submit = client.post(f"/api/plans/{plan['id']}/submit-review")
    assert submit.status_code == 200
    approve = client.post(f"/api/plans/{plan['id']}/approve")
    assert approve.status_code == 200
    return approve.json()

