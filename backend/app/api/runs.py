from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.schemas import RunCreate, RunRead, RunUpdate
from app.services.state_ledger import write_event
from app.api.utils import read_run, require_run

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.post("", response_model=RunRead)
def create_run(payload: RunCreate, db: Session = Depends(get_db)) -> RunRead:
    run = models.Run(name=payload.name, description=payload.description, status="DRAFT")
    db.add(run)
    db.flush()
    write_event(db, run_id=run.id, event_type="RUN_CREATED", payload=payload.model_dump())
    db.commit()
    db.refresh(run)
    return read_run(db, run)


@router.get("", response_model=list[RunRead])
def list_runs(db: Session = Depends(get_db)) -> list[RunRead]:
    runs = db.query(models.Run).order_by(models.Run.created_at.desc()).all()
    return [read_run(db, run) for run in runs]


@router.get("/{run_id}", response_model=RunRead)
def get_run(run_id: str, db: Session = Depends(get_db)) -> RunRead:
    return read_run(db, require_run(db, run_id))


@router.patch("/{run_id}", response_model=RunRead)
def update_run(run_id: str, payload: RunUpdate, db: Session = Depends(get_db)) -> RunRead:
    run = require_run(db, run_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(run, key, value)
    write_event(db, run_id=run.id, event_type="RUN_UPDATED", payload=payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(run)
    return read_run(db, run)


@router.post("/{run_id}/pause", response_model=RunRead)
def pause_run(run_id: str, db: Session = Depends(get_db)) -> RunRead:
    run = require_run(db, run_id)
    run.status = "PAUSED"
    write_event(db, run_id=run.id, plan_id=run.active_plan_id, event_type="RUN_PAUSED", payload={})
    db.commit()
    return read_run(db, run)


@router.post("/{run_id}/resume", response_model=RunRead)
def resume_run(run_id: str, db: Session = Depends(get_db)) -> RunRead:
    run = require_run(db, run_id)
    run.status = "RUNNING"
    write_event(db, run_id=run.id, plan_id=run.active_plan_id, event_type="RUN_RESUMED", payload={})
    db.commit()
    return read_run(db, run)


@router.post("/{run_id}/cancel", response_model=RunRead)
def cancel_run(run_id: str, db: Session = Depends(get_db)) -> RunRead:
    run = require_run(db, run_id)
    run.status = "CANCELED"
    write_event(db, run_id=run.id, plan_id=run.active_plan_id, event_type="RUN_CANCELED", payload={})
    db.commit()
    return read_run(db, run)

