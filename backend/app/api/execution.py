from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import models
from app.db import SessionLocal, get_db
from app.schemas import RunStatusRead, StateLedgerEventRead, TaskExecutionRead, VerificationResultRead
from app.services.autonomy_policy import decide_task_execution
from app.services.scheduler import schedule_run
from app.services.state_ledger import write_event
from app.api.utils import read_run, require_run

router = APIRouter(tags=["execution"])


@router.post("/api/runs/{run_id}/start")
async def start_run(run_id: str, request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    run = require_run(db, run_id)
    if not run.active_plan_id:
        raise HTTPException(status_code=409, detail="Run has no active plan.")
    plan = db.get(models.Plan, run.active_plan_id)
    if not plan or plan.status != "LOCKED":
        raise HTTPException(status_code=409, detail="Execution cannot start until the plan is approved and locked.")
    if run.status == "COMPLETED":
        return {"status": "completed", "run_id": run_id}
    if run.status == "CANCELED":
        raise HTTPException(status_code=409, detail="Canceled runs cannot be started.")
    run.status = "RUNNING"
    write_event(db, run_id=run.id, plan_id=plan.id, event_type="RUN_RESUMED", payload={"source": "start"})
    db.commit()
    schedule_run(request.app, run_id, SessionLocal)
    return {"status": "started", "run_id": run_id}


@router.get("/api/runs/{run_id}/status", response_model=RunStatusRead)
def get_status(run_id: str, db: Session = Depends(get_db)) -> RunStatusRead:
    run = require_run(db, run_id)
    plan = db.get(models.Plan, run.active_plan_id) if run.active_plan_id else None
    reviews = db.query(models.ReviewRecord).filter(models.ReviewRecord.run_id == run_id).order_by(models.ReviewRecord.created_at.desc()).limit(50).all()
    results = db.query(models.VerificationResult).filter(models.VerificationResult.run_id == run_id).order_by(models.VerificationResult.created_at.desc()).limit(50).all()
    events = db.query(models.StateLedgerEvent).filter(models.StateLedgerEvent.run_id == run_id).order_by(models.StateLedgerEvent.created_at.desc()).limit(100).all()
    executions = db.query(models.TaskExecution).filter(models.TaskExecution.run_id == run_id).order_by(models.TaskExecution.started_at.desc()).limit(100).all()
    blocked_reasons = _latest_task_event_reason(db, run_id, "TASK_BLOCKED")
    review_reasons = {
        review.task_id: review.reason
        for review in db.query(models.ReviewRecord)
        .filter(models.ReviewRecord.run_id == run_id, models.ReviewRecord.task_id.isnot(None), models.ReviewRecord.status == "PENDING")
        .all()
        if review.task_id
    }
    policy_summaries = {}
    if plan and run.contract:
        for task in plan.tasks:
            if task.status not in {"SUCCEEDED", "FAILED", "CANCELED", "ROLLED_BACK"}:
                decision = decide_task_execution(db, task=task, plan=plan, contract=run.contract)
                policy_summaries[task.id] = {
                    "decision": decision.decision,
                    "reason": decision.reason,
                    "required_action": decision.required_action,
                }
    return RunStatusRead(
        run=read_run(db, run),
        plan=plan,
        reviews=reviews,
        verification_results=results,
        events=events,
        task_executions=executions,
        blocked_reasons=blocked_reasons,
        review_reasons=review_reasons,
        policy_summaries=policy_summaries,
    )


@router.get("/api/runs/{run_id}/events", response_model=list[StateLedgerEventRead])
def get_events(run_id: str, after_event_id: str | None = None, db: Session = Depends(get_db)) -> list[StateLedgerEventRead]:
    require_run(db, run_id)
    query = db.query(models.StateLedgerEvent).filter(models.StateLedgerEvent.run_id == run_id).order_by(models.StateLedgerEvent.created_at.asc())
    events = query.all()
    if after_event_id:
        seen = False
        filtered = []
        for event in events:
            if seen:
                filtered.append(event)
            elif event.id == after_event_id:
                seen = True
        events = filtered
    return [StateLedgerEventRead.model_validate(event) for event in events]


@router.get("/api/tasks/{task_id}/executions", response_model=list[TaskExecutionRead])
def get_task_executions(task_id: str, db: Session = Depends(get_db)) -> list[TaskExecutionRead]:
    rows = db.query(models.TaskExecution).filter(models.TaskExecution.task_id == task_id).order_by(models.TaskExecution.started_at.desc()).all()
    return [TaskExecutionRead.model_validate(row) for row in rows]


@router.get("/api/tasks/{task_id}/verification-results", response_model=list[VerificationResultRead])
def get_task_verification_results(task_id: str, db: Session = Depends(get_db)) -> list[VerificationResultRead]:
    rows = db.query(models.VerificationResult).filter(models.VerificationResult.task_id == task_id).order_by(models.VerificationResult.created_at.desc()).all()
    return [VerificationResultRead.model_validate(row) for row in rows]


def _latest_task_event_reason(db: Session, run_id: str, event_type: str) -> dict[str, str]:
    rows = (
        db.query(models.StateLedgerEvent)
        .filter(models.StateLedgerEvent.run_id == run_id, models.StateLedgerEvent.event_type == event_type, models.StateLedgerEvent.task_id.isnot(None))
        .order_by(models.StateLedgerEvent.created_at.asc())
        .all()
    )
    reasons: dict[str, str] = {}
    for event in rows:
        if event.task_id:
            reasons[event.task_id] = str(event.payload_json.get("reason") or event.payload_json.get("required_action") or event.payload_json)
    return reasons
