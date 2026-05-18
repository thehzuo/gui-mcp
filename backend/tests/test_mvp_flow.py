from app import models
from app.db import SessionLocal
from app.services.autonomy_policy import decide_task_execution
from app.services.plan_validator import validate_plan


def create_run_with_contract(client):
    run = client.post("/api/runs", json={"name": "MVP flow", "description": "test"}).json()
    client.put(
        f"/api/runs/{run['id']}/contract",
        json={
            "goal": "Build a DAG execution flow.",
            "success_criteria": ["Plan executes"],
            "forbidden_losses": ["No production changes"],
            "allowed_tools": ["mock_executor", "command_executor", "test_runner"],
            "human_approval_boundaries": ["before_plan_execution"],
            "risk_class": "MEDIUM",
            "max_autonomy_level": "L3",
            "notes": "",
        },
    )
    return run


def test_template_plan_validates_and_rejects_cycle(client):
    run = create_run_with_contract(client)
    plan = client.post(f"/api/runs/{run['id']}/plans/generate").json()
    assert client.post(f"/api/plans/{plan['id']}/validate").json()["valid"] is True

    first = plan["tasks"][0]["id"]
    last = plan["tasks"][-1]["id"]
    response = client.post(
        f"/api/plans/{plan['id']}/dependencies",
        json={"from_task_id": last, "to_task_id": first},
    )
    assert response.status_code == 422


def test_plan_lock_prevents_structural_task_edits(client):
    run = create_run_with_contract(client)
    plan = client.post(f"/api/runs/{run['id']}/plans/generate").json()
    client.post(f"/api/plans/{plan['id']}/submit-review")
    client.post(f"/api/plans/{plan['id']}/approve")

    task_id = plan["tasks"][0]["id"]
    response = client.patch(f"/api/tasks/{task_id}", json={"title": "mutate locked task"})
    assert response.status_code == 409


def test_plan_review_queue_approval_locks_plan(client):
    run = create_run_with_contract(client)
    plan = client.post(f"/api/runs/{run['id']}/plans/generate").json()
    client.post(f"/api/plans/{plan['id']}/submit-review")
    review = client.get("/api/reviews?status=PENDING").json()[0]

    client.post(f"/api/reviews/{review['id']}/approve", json={"reviewer": "tester", "comment": "lock it"})
    locked = client.get(f"/api/plans/{plan['id']}").json()

    assert locked["status"] == "LOCKED"
    assert all(task["status"] == "READY" for task in locked["tasks"])


def test_autonomy_policy_requires_review_for_irreversible_task(client):
    run = create_run_with_contract(client)
    plan = client.post(f"/api/runs/{run['id']}/plans/generate").json()
    task_id = plan["tasks"][0]["id"]
    client.patch(f"/api/tasks/{task_id}", json={"reversibility": "IRREVERSIBLE"})
    client.post(f"/api/plans/{plan['id']}/approve")

    db = SessionLocal()
    try:
        task = db.get(models.TaskNode, task_id)
        locked_plan = db.get(models.Plan, plan["id"])
        decision = decide_task_execution(db, task=task, plan=locked_plan, contract=locked_plan.run.contract)
        assert decision.decision == "HUMAN_REVIEW_REQUIRED"
    finally:
        db.close()


def test_scheduler_blocks_on_review_then_completes(client):
    run = create_run_with_contract(client)
    plan = client.post(f"/api/runs/{run['id']}/plans/generate").json()
    client.post(f"/api/plans/{plan['id']}/submit-review")
    client.post(f"/api/plans/{plan['id']}/approve")

    client.post(f"/api/runs/{run['id']}/start")
    import time

    time.sleep(2)
    pending = client.get("/api/reviews?status=PENDING").json()
    assert any(review["review_type"] == "TASK_REVIEW" for review in pending)

    client.post(f"/api/reviews/{pending[0]['id']}/approve", json={"reviewer": "tester", "comment": "ok"})
    client.post(f"/api/runs/{run['id']}/start")
    time.sleep(2)

    status = client.get(f"/api/runs/{run['id']}/status").json()
    assert status["run"]["status"] == "COMPLETED"
    assert status["run"]["progress_summary"]["SUCCEEDED"] == 5
    assert any(event["event_type"] == "RUN_COMPLETED" for event in status["events"])


def test_command_executor_records_output(client):
    run = create_run_with_contract(client)
    plan = client.post(f"/api/runs/{run['id']}/plans/generate").json()
    task_id = plan["tasks"][0]["id"]
    client.patch(
        f"/api/tasks/{task_id}",
        json={
            "executor_type": "command",
            "tool_refs": ["command_executor"],
            "executor_config_json": {"command": "printf loom"},
        },
    )
    client.post(f"/api/plans/{plan['id']}/approve")
    client.post(f"/api/runs/{run['id']}/start")
    import time

    time.sleep(1)
    executions = client.get(f"/api/tasks/{task_id}/executions").json()
    assert executions[0]["exit_code"] == 0
    assert executions[0]["stdout"] == "loom"
