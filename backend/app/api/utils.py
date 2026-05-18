from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.schemas import RunRead


def require_run(db: Session, run_id: str) -> models.Run:
    run = db.get(models.Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    return run


def require_plan(db: Session, plan_id: str) -> models.Plan:
    plan = db.get(models.Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found.")
    return plan


def require_task(db: Session, task_id: str) -> models.TaskNode:
    task = db.get(models.TaskNode, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


def require_editable_plan(plan: models.Plan) -> None:
    if plan.status not in {"DRAFT", "AWAITING_REVIEW"}:
        raise HTTPException(status_code=409, detail="Plan is locked or no longer editable. Create a new plan version.")


def run_progress(db: Session, run_id: str) -> dict[str, int]:
    rows = db.query(models.TaskNode.status).filter(models.TaskNode.run_id == run_id).all()
    summary: dict[str, int] = {}
    for (status,) in rows:
        summary[status] = summary.get(status, 0) + 1
    return summary


def read_run(db: Session, run: models.Run) -> RunRead:
    payload = RunRead.model_validate(run)
    payload.progress_summary = run_progress(db, run.id)
    return payload

