import asyncio

from app import models
from app.db import SessionLocal
from app.services.scheduler import run_scheduler_loop, run_scheduler_once
from tests.helpers import create_run_with_contract, generate_and_lock_plan


def task_statuses(plan_id: str) -> dict[str, str]:
    db = SessionLocal()
    try:
        return {task.title: task.status for task in db.query(models.TaskNode).filter(models.TaskNode.plan_id == plan_id).all()}
    finally:
        db.close()


def test_failed_command_blocks_downstream_tasks(client):
    run = create_run_with_contract(client)
    plan = client.post(f"/api/runs/{run['id']}/plans/generate").json()
    first_task_id = plan["tasks"][0]["id"]
    client.patch(
        f"/api/tasks/{first_task_id}",
        json={
            "executor_type": "command",
            "tool_refs": ["command_executor"],
            "executor_config_json": {"command": "exit 7"},
        },
    )
    locked = client.post(f"/api/plans/{plan['id']}/approve").json()

    asyncio.run(run_scheduler_loop(run["id"], SessionLocal, max_rounds=12))

    statuses = task_statuses(locked["id"])
    assert statuses["Inspect current mission boundary"] == "FAILED"
    assert statuses["Design durable state changes"] == "BLOCKED"

    status = client.get(f"/api/runs/{run['id']}/status").json()
    assert status["run"]["status"] == "FAILED"
    assert any(event["event_type"] == "TASK_FAILED" for event in status["events"])
    assert any(event["event_type"] == "TASK_BLOCKED" for event in status["events"])


def test_paused_and_canceled_runs_do_not_schedule_tasks(client):
    run = create_run_with_contract(client)
    plan = generate_and_lock_plan(client, run["id"])

    client.post(f"/api/runs/{run['id']}/pause")
    assert asyncio.run(run_scheduler_once(run["id"], SessionLocal)) is False
    assert all(status == "READY" for status in task_statuses(plan["id"]).values())

    client.post(f"/api/runs/{run['id']}/resume")
    client.post(f"/api/runs/{run['id']}/cancel")
    assert asyncio.run(run_scheduler_once(run["id"], SessionLocal)) is False
    assert all(status == "READY" for status in task_statuses(plan["id"]).values())


def test_manual_verifier_creates_review_and_approval_completes_task(client):
    run = create_run_with_contract(client)
    plan = client.post(f"/api/runs/{run['id']}/plans/generate").json()
    first_task_id = plan["tasks"][0]["id"]
    client.patch(f"/api/tasks/{first_task_id}", json={"verifier_refs": ["manual_verifier"]})
    client.post(f"/api/plans/{plan['id']}/approve")

    asyncio.run(run_scheduler_loop(run["id"], SessionLocal, max_rounds=3))

    pending = client.get("/api/reviews?status=PENDING").json()
    manual_review = next(review for review in pending if review["task_id"] == first_task_id)
    assert "Manual verification" in manual_review["reason"]

    client.post(f"/api/reviews/{manual_review['id']}/approve", json={"reviewer": "tester", "comment": "verified"})
    task = client.get(f"/api/plans/{plan['id']}").json()["tasks"][0]
    assert task["status"] == "SUCCEEDED"
    assert task["review_status"] == "APPROVED"

    asyncio.run(run_scheduler_loop(run["id"], SessionLocal, max_rounds=20))
    status = client.get(f"/api/runs/{run['id']}/status").json()
    assert status["run"]["status"] in {"RUNNING", "COMPLETED"}


def test_start_endpoint_is_idempotent_for_completed_tasks(client):
    run = create_run_with_contract(client)
    plan = generate_and_lock_plan(client, run["id"])

    client.post(f"/api/runs/{run['id']}/start")
    client.post(f"/api/runs/{run['id']}/start")

    import time

    time.sleep(1.5)
    db = SessionLocal()
    try:
        first_task_id = plan["tasks"][0]["id"]
        executions = db.query(models.TaskExecution).filter(models.TaskExecution.task_id == first_task_id).all()
        assert len(executions) == 1
    finally:
        db.close()
