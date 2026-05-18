from __future__ import annotations

import asyncio
from datetime import timezone

from sqlalchemy.orm import Session, sessionmaker

from app import models
from app.models import utcnow
from app.services.autonomy_policy import decide_task_execution
from app.services.executor import execute_task
from app.services.review import create_task_review
from app.services.state_ledger import write_event
from app.services.verifier import verify_task

TERMINAL_TASK_STATUSES = {"SUCCEEDED", "FAILED", "CANCELED", "ROLLED_BACK"}


def dependency_ids(db: Session, plan_id: str, task_id: str) -> list[str]:
    deps = (
        db.query(models.TaskDependency)
        .filter(models.TaskDependency.plan_id == plan_id, models.TaskDependency.to_task_id == task_id)
        .all()
    )
    return [dep.from_task_id for dep in deps]


def dependencies_succeeded(db: Session, plan_id: str, task_id: str) -> bool:
    ids = dependency_ids(db, plan_id, task_id)
    if not ids:
        return True
    succeeded = (
        db.query(models.TaskNode)
        .filter(models.TaskNode.id.in_(ids), models.TaskNode.status == "SUCCEEDED")
        .count()
    )
    return succeeded == len(ids)


def dependency_failed(db: Session, plan_id: str, task_id: str) -> bool:
    ids = dependency_ids(db, plan_id, task_id)
    if not ids:
        return False
    failed = (
        db.query(models.TaskNode)
        .filter(models.TaskNode.id.in_(ids), models.TaskNode.status.in_(["FAILED", "CANCELED", "REJECTED"]))
        .count()
    )
    return failed > 0


async def run_scheduler_loop(run_id: str, session_factory: sessionmaker, max_rounds: int = 100) -> None:
    for _ in range(max_rounds):
        progressed = await run_scheduler_once(run_id, session_factory)
        if not progressed:
            return
        await asyncio.sleep(0.05)


async def run_scheduler_once(run_id: str, session_factory: sessionmaker) -> bool:
    db = session_factory()
    try:
        run = db.get(models.Run, run_id)
        if not run or run.status in {"PAUSED", "CANCELED", "COMPLETED"}:
            return False
        plan = db.get(models.Plan, run.active_plan_id) if run.active_plan_id else None
        if not plan or plan.status != "LOCKED":
            return False
        contract = run.contract
        tasks = (
            db.query(models.TaskNode)
            .filter(models.TaskNode.plan_id == plan.id)
            .order_by(models.TaskNode.created_at.asc())
            .all()
        )
        progressed = False
        for task in tasks:
            if task.status in TERMINAL_TASK_STATUSES or task.status in {"RUNNING", "VERIFYING", "QUEUED"}:
                continue
            if dependency_failed(db, plan.id, task.id):
                if task.status != "BLOCKED":
                    task.status = "BLOCKED"
                    write_event(db, run_id=run.id, plan_id=plan.id, task_id=task.id, event_type="TASK_BLOCKED", payload={"reason": "Dependency failed."})
                    progressed = True
                continue
            if not dependencies_succeeded(db, plan.id, task.id):
                if task.status not in {"BLOCKED", "AWAITING_REVIEW"}:
                    task.status = "BLOCKED"
                    write_event(db, run_id=run.id, plan_id=plan.id, task_id=task.id, event_type="TASK_BLOCKED", payload={"reason": "Waiting on dependencies."})
                    progressed = True
                continue
            if task.review_status == "PENDING":
                if task.status not in {"AWAITING_REVIEW", "NEEDS_HUMAN"}:
                    task.status = "AWAITING_REVIEW"
                    progressed = True
                continue
            decision = decide_task_execution(db, task=task, plan=plan, contract=contract)
            if decision.decision == "BLOCKED":
                if task.status != "BLOCKED":
                    task.status = "BLOCKED"
                    write_event(db, run_id=run.id, plan_id=plan.id, task_id=task.id, event_type="TASK_BLOCKED", payload=decision.__dict__)
                    progressed = True
                continue
            if decision.decision == "HUMAN_REVIEW_REQUIRED":
                create_task_review(db, task, reason=decision.reason, policy_decision=decision.decision)
                progressed = True
                continue
            await _execute_and_verify(db, task)
            progressed = True
            break

        _refresh_run_status(db, run, plan)
        db.commit()
        return progressed
    finally:
        db.close()


async def _execute_and_verify(db: Session, task: models.TaskNode) -> None:
    task.status = "QUEUED"
    write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type="TASK_QUEUED", payload={})
    db.flush()

    task.status = "RUNNING"
    write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type="TASK_STARTED", payload={})
    execution = models.TaskExecution(
        task_id=task.id,
        run_id=task.run_id,
        executor_type=task.executor_type,
        status="RUNNING",
    )
    db.add(execution)
    db.flush()
    db.commit()

    output = await execute_task(task)

    execution.status = output.status
    execution.command = output.command
    execution.stdout = output.stdout
    execution.stderr = output.stderr
    execution.exit_code = output.exit_code
    execution.duration_ms = output.duration_ms
    execution.output_json = output.output_json
    execution.finished_at = utcnow().astimezone(timezone.utc)
    write_event(
        db,
        run_id=task.run_id,
        plan_id=task.plan_id,
        task_id=task.id,
        event_type="TASK_OUTPUT_RECORDED",
        payload={"execution_id": execution.id, "exit_code": execution.exit_code, "duration_ms": execution.duration_ms},
    )

    task.status = "VERIFYING"
    write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type="TASK_VERIFYING", payload={})
    results = verify_task(db, task, execution)
    failed = any(result.status == "FAIL" for result in results)
    manual = any(result.evidence_json.get("requires_human") for result in results)
    unknown_only = results and all(result.status == "UNKNOWN" for result in results)

    if failed or execution.status == "FAILED":
        task.status = "FAILED"
        write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type="TASK_VERIFICATION_FAILED", payload={"execution_id": execution.id})
        write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type="TASK_FAILED", payload={"execution_id": execution.id})
    elif manual:
        task.status = "NEEDS_HUMAN"
        task.review_status = "PENDING"
        write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type="TASK_VERIFICATION_FAILED", payload={"reason": "Manual verifier requires human review."})
        create_task_review(
            db,
            task,
            reason="Manual verification is required before this task can be considered complete.",
            policy_decision="HUMAN_REVIEW_REQUIRED",
        )
    else:
        task.status = "SUCCEEDED"
        event = "TASK_VERIFICATION_PASSED" if not unknown_only else "TASK_VERIFICATION_UNKNOWN"
        write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type=event, payload={"execution_id": execution.id})
        write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type="TASK_SUCCEEDED", payload={"execution_id": execution.id})


def _refresh_run_status(db: Session, run: models.Run, plan: models.Plan) -> None:
    statuses = [row[0] for row in db.query(models.TaskNode.status).filter(models.TaskNode.plan_id == plan.id).all()]
    if statuses and all(status == "SUCCEEDED" for status in statuses):
        if run.status != "COMPLETED":
            run.status = "COMPLETED"
            write_event(db, run_id=run.id, plan_id=plan.id, event_type="RUN_COMPLETED", payload={})
    elif any(status == "FAILED" for status in statuses):
        run.status = "FAILED"
    elif run.status not in {"PAUSED", "CANCELED"}:
        run.status = "RUNNING"
