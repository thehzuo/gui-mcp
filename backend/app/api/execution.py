from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import models
from app.db import SessionLocal, get_db
from app.schemas import RunStatusRead, StateLedgerEventRead, TaskExecutionRead, VerificationResultRead
from app.services.scheduler import run_scheduler_loop
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
    run.status = "RUNNING"
    write_event(db, run_id=run.id, plan_id=plan.id, event_type="RUN_RESUMED", payload={"source": "start"})
    db.commit()
    tasks = getattr(request.app.state, "scheduler_tasks", {})
    existing = tasks.get(run_id)
    if not existing or existing.done():
        tasks[run_id] = asyncio.create_task(run_scheduler_loop(run_id, SessionLocal))
        request.app.state.scheduler_tasks = tasks
    return {"status": "started", "run_id": run_id}


@router.get("/api/runs/{run_id}/status", response_model=RunStatusRead)
def get_status(run_id: str, db: Session = Depends(get_db)) -> RunStatusRead:
    run = require_run(db, run_id)
    plan = db.get(models.Plan, run.active_plan_id) if run.active_plan_id else None
    reviews = db.query(models.ReviewRecord).filter(models.ReviewRecord.run_id == run_id).order_by(models.ReviewRecord.created_at.desc()).limit(50).all()
    results = db.query(models.VerificationResult).filter(models.VerificationResult.run_id == run_id).order_by(models.VerificationResult.created_at.desc()).limit(50).all()
    events = db.query(models.StateLedgerEvent).filter(models.StateLedgerEvent.run_id == run_id).order_by(models.StateLedgerEvent.created_at.desc()).limit(100).all()
    return RunStatusRead(
        run=read_run(db, run),
        plan=plan,
        reviews=reviews,
        verification_results=results,
        events=events,
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
