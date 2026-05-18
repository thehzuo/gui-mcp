from tests.helpers import create_run_with_contract


def test_run_contract_plan_task_dependency_crud(client):
    run = create_run_with_contract(client)

    listed_runs = client.get("/api/runs").json()
    assert any(item["id"] == run["id"] for item in listed_runs)

    updated = client.patch(f"/api/runs/{run['id']}", json={"name": "Renamed run"}).json()
    assert updated["name"] == "Renamed run"

    contract = client.get(f"/api/runs/{run['id']}/contract").json()
    assert contract["goal"] == "Build a DAG execution flow."

    plan = client.post(f"/api/runs/{run['id']}/plans/generate").json()
    patched_plan = client.patch(f"/api/plans/{plan['id']}", json={"summary": "Edited summary"}).json()
    assert patched_plan["summary"] == "Edited summary"

    task_payload = {
        "title": "API-created task",
        "description": "Task created through the task CRUD API.",
        "task_family": "code_analysis",
        "risk_level": "LOW",
        "reversibility": "REVERSIBLE",
        "required_autonomy_level": "L3",
        "expected_outputs": ["CRUD output"],
        "verifier_refs": ["command_exit_code"],
        "tool_refs": ["mock_executor"],
        "executor_type": "mock",
        "position_x": 120,
        "position_y": 160,
    }
    created_task = client.post(f"/api/plans/{plan['id']}/tasks", json=task_payload).json()
    assert created_task["title"] == "API-created task"

    updated_task = client.patch(f"/api/tasks/{created_task['id']}", json={"risk_level": "MEDIUM"}).json()
    assert updated_task["risk_level"] == "MEDIUM"

    dependency = client.post(
        f"/api/plans/{plan['id']}/dependencies",
        json={"from_task_id": plan["tasks"][0]["id"], "to_task_id": created_task["id"]},
    ).json()
    assert dependency["from_task_id"] == plan["tasks"][0]["id"]

    delete_dep = client.delete(f"/api/dependencies/{dependency['id']}")
    assert delete_dep.status_code == 200

    delete_task = client.delete(f"/api/tasks/{created_task['id']}")
    assert delete_task.status_code == 200

    events = client.get(f"/api/runs/{run['id']}/events").json()
    event_types = [event["event_type"] for event in events]
    assert "RUN_CREATED" in event_types
    assert "TASK_CONTRACT_CREATED" in event_types
    assert "PLAN_GENERATED" in event_types
    assert "TASK_ADDED" in event_types
    assert "TASK_DEPENDENCY_ADDED" in event_types
    assert "TASK_DEPENDENCY_REMOVED" in event_types


def test_execution_cannot_start_until_plan_is_locked(client):
    run = create_run_with_contract(client)
    plan = client.post(f"/api/runs/{run['id']}/plans/generate").json()

    response = client.post(f"/api/runs/{run['id']}/start")
    assert response.status_code == 409
    assert "approved and locked" in response.json()["detail"]

    client.post(f"/api/plans/{plan['id']}/approve")
    assert client.post(f"/api/runs/{run['id']}/start").status_code == 200


def test_pause_resume_cancel_mutate_run_status_and_ledger(client):
    run = create_run_with_contract(client)

    assert client.post(f"/api/runs/{run['id']}/pause").json()["status"] == "PAUSED"
    assert client.post(f"/api/runs/{run['id']}/resume").json()["status"] == "RUNNING"
    assert client.post(f"/api/runs/{run['id']}/cancel").json()["status"] == "CANCELED"

    events = [event["event_type"] for event in client.get(f"/api/runs/{run['id']}/events").json()]
    assert "RUN_PAUSED" in events
    assert "RUN_RESUMED" in events
    assert "RUN_CANCELED" in events
