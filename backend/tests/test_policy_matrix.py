from app import models
from app.db import SessionLocal
from app.services.autonomy_policy import decide_task_execution
from tests.helpers import create_run_with_contract


def policy_for_first_task(client, *, task_patch: dict | None = None, contract_max: str = "L3", allowed_tools: list[str] | None = None):
    run = create_run_with_contract(client, max_autonomy_level=contract_max, allowed_tools=allowed_tools)
    plan = client.post(f"/api/runs/{run['id']}/plans/generate").json()
    task_id = plan["tasks"][0]["id"]
    if task_patch:
        response = client.patch(f"/api/tasks/{task_id}", json=task_patch)
        assert response.status_code == 200
    locked = client.post(f"/api/plans/{plan['id']}/approve").json()

    db = SessionLocal()
    try:
        task = db.get(models.TaskNode, task_id)
        plan_obj = db.get(models.Plan, locked["id"])
        return decide_task_execution(db, task=task, plan=plan_obj, contract=plan_obj.run.contract)
    finally:
        db.close()


def test_policy_blocks_unlocked_plan(client):
    run = create_run_with_contract(client)
    plan = client.post(f"/api/runs/{run['id']}/plans/generate").json()
    task_id = plan["tasks"][0]["id"]

    db = SessionLocal()
    try:
        task = db.get(models.TaskNode, task_id)
        plan_obj = db.get(models.Plan, plan["id"])
        decision = decide_task_execution(db, task=task, plan=plan_obj, contract=plan_obj.run.contract)
        assert decision.decision == "BLOCKED"
    finally:
        db.close()


def test_policy_requires_review_for_critical_risk(client):
    decision = policy_for_first_task(client, task_patch={"risk_level": "CRITICAL"})
    assert decision.decision == "HUMAN_REVIEW_REQUIRED"
    assert "CRITICAL" in decision.reason


def test_policy_requires_review_for_irreversible_task(client):
    decision = policy_for_first_task(client, task_patch={"reversibility": "IRREVERSIBLE"})
    assert decision.decision == "HUMAN_REVIEW_REQUIRED"
    assert "irreversible" in decision.reason.lower()


def test_policy_requires_review_for_high_risk_weak_verifier(client):
    decision = policy_for_first_task(client, task_patch={"risk_level": "HIGH", "verifier_refs": ["noop"]})
    assert decision.decision == "HUMAN_REVIEW_REQUIRED"
    assert "high risk" in decision.reason.lower()


def test_policy_requires_review_when_contract_autonomy_is_too_low(client):
    decision = policy_for_first_task(client, contract_max="L2")
    assert decision.decision == "HUMAN_REVIEW_REQUIRED"
    assert "Task Contract" in decision.reason


def test_policy_requires_review_when_model_capability_is_too_low(client):
    decision = policy_for_first_task(client, task_patch={"task_family": "deployment", "required_autonomy_level": "L3"})
    assert decision.decision == "HUMAN_REVIEW_REQUIRED"
    assert "capability" in decision.reason


def test_policy_blocks_tools_outside_task_contract(client):
    decision = policy_for_first_task(
        client,
        allowed_tools=["mock_executor"],
        task_patch={"executor_type": "command", "tool_refs": ["command_executor"]},
    )
    assert decision.decision == "BLOCKED"
    assert "outside the Task Contract" in decision.reason


def test_policy_allows_low_risk_verified_task(client):
    decision = policy_for_first_task(client, task_patch={"risk_level": "LOW", "verifier_refs": ["command_exit_code"]})
    assert decision.decision == "AUTO_EXECUTE"
