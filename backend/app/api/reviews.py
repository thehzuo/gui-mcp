from __future__ import annotations

from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.models import utcnow
from app.schemas import ReviewDecision, ReviewRead
from app.services.plan_validator import validate_plan
from app.services.state_ledger import write_event

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("", response_model=list[ReviewRead])
def list_reviews(status: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[ReviewRead]:
    query = db.query(models.ReviewRecord)
    if status:
        query = query.filter(models.ReviewRecord.status == status)
    reviews = query.order_by(models.ReviewRecord.created_at.asc()).all()
    return [ReviewRead.model_validate(review) for review in reviews]


@router.post("/{review_id}/approve", response_model=ReviewRead)
def approve_review(review_id: str, payload: ReviewDecision, db: Session = Depends(get_db)) -> ReviewRead:
    review = _require_review(db, review_id)
    review.status = "APPROVED"
    review.decision = "APPROVED"
    review.reviewer = payload.reviewer
    review.comment = payload.comment
    if review.task_id:
        task = db.get(models.TaskNode, review.task_id)
        if task:
            task.review_status = "APPROVED"
            if task.status == "NEEDS_HUMAN":
                task.status = "SUCCEEDED"
                write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type="TASK_APPROVED", payload=payload.model_dump())
                write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type="TASK_SUCCEEDED", payload={"via": "manual_verifier"})
            elif task.status in {"AWAITING_REVIEW", "BLOCKED"}:
                task.status = "READY"
                write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type="TASK_APPROVED", payload=payload.model_dump())
    if review.plan_id and review.review_type == "PLAN_REVIEW":
        plan = db.get(models.Plan, review.plan_id)
        if plan:
            result = validate_plan(db, plan.id)
            if not result.valid:
                raise HTTPException(status_code=422, detail=result.errors)
            now = utcnow().astimezone(timezone.utc)
            plan.status = "LOCKED"
            plan.approved_by = payload.reviewer
            plan.approved_at = now
            plan.locked_at = now
            plan.run.status = "PLAN_APPROVED"
            plan.run.active_plan_id = plan.id
            for task in plan.tasks:
                if task.status == "DRAFT":
                    task.status = "READY"
            write_event(db, run_id=review.run_id, plan_id=review.plan_id, event_type="PLAN_APPROVED", payload={"via": "review_queue", "approved_by": payload.reviewer})
    db.commit()
    db.refresh(review)
    return ReviewRead.model_validate(review)


@router.post("/{review_id}/reject", response_model=ReviewRead)
def reject_review(review_id: str, payload: ReviewDecision, db: Session = Depends(get_db)) -> ReviewRead:
    review = _require_review(db, review_id)
    review.status = "REJECTED"
    review.decision = "REJECTED"
    review.reviewer = payload.reviewer
    review.comment = payload.comment
    if review.task_id:
        task = db.get(models.TaskNode, review.task_id)
        if task:
            task.review_status = "REJECTED"
            task.status = "FAILED"
            write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type="TASK_REJECTED", payload=payload.model_dump())
    elif review.plan_id:
        plan = db.get(models.Plan, review.plan_id)
        if plan:
            plan.status = "REJECTED"
            plan.run.status = "PLANNING"
            write_event(db, run_id=plan.run_id, plan_id=plan.id, event_type="PLAN_REJECTED", payload=payload.model_dump())
    db.commit()
    db.refresh(review)
    return ReviewRead.model_validate(review)


@router.post("/{review_id}/request-changes", response_model=ReviewRead)
def request_changes(review_id: str, payload: ReviewDecision, db: Session = Depends(get_db)) -> ReviewRead:
    review = _require_review(db, review_id)
    review.status = "CHANGES_REQUESTED"
    review.decision = "CHANGES_REQUESTED"
    review.reviewer = payload.reviewer
    review.comment = payload.comment
    write_event(db, run_id=review.run_id, plan_id=review.plan_id, task_id=review.task_id, event_type="HUMAN_OVERRIDE", payload=payload.model_dump())
    db.commit()
    db.refresh(review)
    return ReviewRead.model_validate(review)


def _require_review(db: Session, review_id: str) -> models.ReviewRecord:
    review = db.get(models.ReviewRecord, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    return review
