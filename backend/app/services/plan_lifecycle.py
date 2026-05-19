from __future__ import annotations

from datetime import timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.models import utcnow
from app.services.plan_validator import validate_plan
from app.services.state_ledger import write_event


def approve_plan_version(db: Session, plan: models.Plan, *, approved_by: str, via: str = "direct") -> models.Plan:
    result = validate_plan(db, plan.id)
    if not result.valid:
        raise HTTPException(status_code=422, detail=result.errors)

    now = utcnow().astimezone(timezone.utc)
    previous_active_id = plan.run.active_plan_id
    previous_active = db.get(models.Plan, previous_active_id) if previous_active_id and previous_active_id != plan.id else None

    plan.status = "LOCKED"
    plan.approved_by = approved_by
    plan.approved_at = now
    plan.locked_at = now
    plan.run.status = "PLAN_APPROVED"
    plan.run.active_plan_id = plan.id

    for task in plan.tasks:
        if task.status == "DRAFT":
            task.status = "READY"

    if previous_active and previous_active.status == "LOCKED":
        previous_active.status = "SUPERSEDED"
        write_event(
            db,
            run_id=previous_active.run_id,
            plan_id=previous_active.id,
            event_type="PLAN_SUPERSEDED",
            payload={"superseded_by_plan_id": plan.id},
        )

    for review in (
        db.query(models.ReviewRecord)
        .filter(
            models.ReviewRecord.plan_id == plan.id,
            models.ReviewRecord.review_type == "PLAN_REVIEW",
            models.ReviewRecord.status == "PENDING",
        )
        .all()
    ):
        review.status = "APPROVED"
        review.decision = "APPROVED"
        review.reviewer = approved_by

    write_event(
        db,
        run_id=plan.run_id,
        plan_id=plan.id,
        event_type="PLAN_APPROVED",
        payload={"approved_by": approved_by, "via": via},
    )
    return plan


def revise_locked_plan(db: Session, source: models.Plan) -> models.Plan:
    if source.status != "LOCKED":
        raise HTTPException(status_code=409, detail="Only locked plans can be revised into a new draft version.")

    version = (db.query(models.Plan).filter(models.Plan.run_id == source.run_id).count() or 0) + 1
    revised = models.Plan(
        run_id=source.run_id,
        version=version,
        status="DRAFT",
        summary=f"Revision of plan v{source.version}: {source.summary}",
        assumptions=list(source.assumptions or []),
        open_questions=list(source.open_questions or []),
        created_by="manual_revision",
    )
    db.add(revised)
    db.flush()

    task_id_map: dict[str, str] = {}
    for task in source.tasks:
        cloned_task = models.TaskNode(
            run_id=source.run_id,
            plan_id=revised.id,
            title=task.title,
            description=task.description,
            task_family=task.task_family,
            status="DRAFT",
            review_status="NOT_REQUIRED",
            risk_level=task.risk_level,
            reversibility=task.reversibility,
            required_autonomy_level=task.required_autonomy_level,
            assigned_model_id=task.assigned_model_id,
            expected_outputs=list(task.expected_outputs or []),
            verifier_refs=list(task.verifier_refs or []),
            tool_refs=list(task.tool_refs or []),
            executor_type=task.executor_type,
            executor_config_json=dict(task.executor_config_json or {}),
            human_review_required=task.human_review_required,
            position_x=task.position_x + 36,
            position_y=task.position_y + 36,
        )
        db.add(cloned_task)
        db.flush()
        task_id_map[task.id] = cloned_task.id

    for dependency in source.dependencies:
        if dependency.from_task_id in task_id_map and dependency.to_task_id in task_id_map:
            db.add(
                models.TaskDependency(
                    plan_id=revised.id,
                    from_task_id=task_id_map[dependency.from_task_id],
                    to_task_id=task_id_map[dependency.to_task_id],
                )
            )

    write_event(
        db,
        run_id=source.run_id,
        plan_id=revised.id,
        event_type="PLAN_REVISED",
        payload={"source_plan_id": source.id, "source_version": source.version, "version": revised.version},
    )
    return revised
