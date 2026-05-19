from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.schemas import PlanPatch, PlanRead, ValidationResult
from app.services.plan_lifecycle import approve_plan_version, revise_locked_plan
from app.services.plan_validator import validate_plan
from app.services.planner import generate_template_plan
from app.services.review import create_plan_review
from app.services.state_ledger import write_event
from app.api.utils import require_editable_plan, require_plan, require_run

router = APIRouter(tags=["plans"])


@router.post("/api/runs/{run_id}/plans/generate", response_model=PlanRead)
def generate_plan(run_id: str, db: Session = Depends(get_db)) -> PlanRead:
    run = require_run(db, run_id)
    if not run.contract:
        raise HTTPException(status_code=409, detail="Create a Task Contract before generating a plan.")
    plan = generate_template_plan(db, run)
    db.commit()
    db.refresh(plan)
    return PlanRead.model_validate(plan)


@router.get("/api/runs/{run_id}/plans", response_model=list[PlanRead])
def list_plans(run_id: str, db: Session = Depends(get_db)) -> list[PlanRead]:
    require_run(db, run_id)
    plans = db.query(models.Plan).filter(models.Plan.run_id == run_id).order_by(models.Plan.version.asc()).all()
    return [PlanRead.model_validate(plan) for plan in plans]


@router.get("/api/plans/{plan_id}", response_model=PlanRead)
def get_plan(plan_id: str, db: Session = Depends(get_db)) -> PlanRead:
    return PlanRead.model_validate(require_plan(db, plan_id))


@router.patch("/api/plans/{plan_id}", response_model=PlanRead)
def patch_plan(plan_id: str, payload: PlanPatch, db: Session = Depends(get_db)) -> PlanRead:
    plan = require_plan(db, plan_id)
    require_editable_plan(plan)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(plan, key, value)
    write_event(db, run_id=plan.run_id, plan_id=plan.id, event_type="PLAN_EDITED", payload=payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(plan)
    return PlanRead.model_validate(plan)


@router.post("/api/plans/{plan_id}/revise", response_model=PlanRead)
def revise_plan(plan_id: str, db: Session = Depends(get_db)) -> PlanRead:
    source = require_plan(db, plan_id)
    revised = revise_locked_plan(db, source)
    db.commit()
    db.refresh(revised)
    return PlanRead.model_validate(revised)


@router.post("/api/plans/{plan_id}/validate", response_model=ValidationResult)
def validate_plan_endpoint(plan_id: str, db: Session = Depends(get_db)) -> ValidationResult:
    require_plan(db, plan_id)
    return validate_plan(db, plan_id)


@router.post("/api/plans/{plan_id}/submit-review", response_model=PlanRead)
def submit_plan_review(plan_id: str, db: Session = Depends(get_db)) -> PlanRead:
    plan = require_plan(db, plan_id)
    require_editable_plan(plan)
    result = validate_plan(db, plan.id)
    if not result.valid:
        raise HTTPException(status_code=422, detail=result.errors)
    plan.status = "AWAITING_REVIEW"
    plan.run.status = "AWAITING_PLAN_REVIEW"
    create_plan_review(db, plan)
    db.commit()
    db.refresh(plan)
    return PlanRead.model_validate(plan)


@router.post("/api/plans/{plan_id}/approve", response_model=PlanRead)
def approve_plan(plan_id: str, db: Session = Depends(get_db)) -> PlanRead:
    plan = require_plan(db, plan_id)
    approve_plan_version(db, plan, approved_by="local-reviewer", via="direct")
    db.commit()
    db.refresh(plan)
    return PlanRead.model_validate(plan)


@router.post("/api/plans/{plan_id}/reject", response_model=PlanRead)
def reject_plan(plan_id: str, db: Session = Depends(get_db)) -> PlanRead:
    plan = require_plan(db, plan_id)
    plan.status = "REJECTED"
    plan.run.status = "PLANNING"
    for review in db.query(models.ReviewRecord).filter(models.ReviewRecord.plan_id == plan.id, models.ReviewRecord.status == "PENDING").all():
        review.status = "REJECTED"
        review.decision = "REJECTED"
    write_event(db, run_id=plan.run_id, plan_id=plan.id, event_type="PLAN_REJECTED", payload={})
    db.commit()
    db.refresh(plan)
    return PlanRead.model_validate(plan)
