from __future__ import annotations

from sqlalchemy.orm import Session

from app import models
from app.services.state_ledger import write_event
from app.services.verifier import verifier_strength


def create_plan_review(db: Session, plan: models.Plan, reason: str = "Plan-level review required.") -> models.ReviewRecord:
    existing = (
        db.query(models.ReviewRecord)
        .filter(
            models.ReviewRecord.plan_id == plan.id,
            models.ReviewRecord.review_type == "PLAN_REVIEW",
            models.ReviewRecord.status == "PENDING",
        )
        .first()
    )
    if existing:
        return existing
    tasks = list(plan.tasks)
    packet = {
        "run_goal": plan.run.contract.goal if plan.run.contract else "",
        "plan_summary": plan.summary,
        "task_count": len(tasks),
        "dependency_count": len(plan.dependencies),
        "high_risk_task_count": len([task for task in tasks if task.risk_level in {"HIGH", "CRITICAL"}]),
        "tasks_requiring_human_approval": [task.title for task in tasks if task.human_review_required],
        "open_questions": plan.open_questions,
        "assumptions": plan.assumptions,
        "policy_warnings": [],
    }
    review = models.ReviewRecord(
        run_id=plan.run_id,
        plan_id=plan.id,
        review_type="PLAN_REVIEW",
        reason=reason,
        packet_json=packet,
    )
    db.add(review)
    write_event(db, run_id=plan.run_id, plan_id=plan.id, event_type="PLAN_SUBMITTED_FOR_REVIEW", payload=packet)
    return review


def create_task_review(
    db: Session,
    task: models.TaskNode,
    *,
    reason: str,
    policy_decision: str,
) -> models.ReviewRecord:
    existing = (
        db.query(models.ReviewRecord)
        .filter(
            models.ReviewRecord.task_id == task.id,
            models.ReviewRecord.review_type == "TASK_REVIEW",
            models.ReviewRecord.status == "PENDING",
        )
        .first()
    )
    if existing:
        return existing
    packet = {
        "task_title": task.title,
        "task_description": task.description,
        "why_review_is_required": reason,
        "expected_outputs": task.expected_outputs,
        "proposed_execution_mode": task.executor_type,
        "risk_level": task.risk_level,
        "reversibility": task.reversibility,
        "verifier_coverage": verifier_strength(task.verifier_refs or []),
        "policy_decision": policy_decision,
        "recommended_decision": "Approve if the task remains inside the Task Contract boundaries.",
    }
    review = models.ReviewRecord(
        run_id=task.run_id,
        plan_id=task.plan_id,
        task_id=task.id,
        review_type="TASK_REVIEW",
        reason=reason,
        packet_json=packet,
    )
    db.add(review)
    task.review_status = "PENDING"
    if task.status != "NEEDS_HUMAN":
        task.status = "AWAITING_REVIEW"
    write_event(
        db,
        run_id=task.run_id,
        plan_id=task.plan_id,
        task_id=task.id,
        event_type="TASK_REVIEW_REQUESTED",
        payload=packet,
    )
    return review
