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
    task_by_id = {task.id: task for task in tasks}
    dependencies = [
        {
            "from_task_id": dep.from_task_id,
            "from_title": task_by_id[dep.from_task_id].title if dep.from_task_id in task_by_id else dep.from_task_id,
            "to_task_id": dep.to_task_id,
            "to_title": task_by_id[dep.to_task_id].title if dep.to_task_id in task_by_id else dep.to_task_id,
        }
        for dep in plan.dependencies
    ]
    packet = {
        "run_goal": plan.run.contract.goal if plan.run.contract else "",
        "plan_summary": plan.summary,
        "task_count": len(tasks),
        "dependency_count": len(plan.dependencies),
        "dependencies": dependencies,
        "expected_outputs": {task.title: task.expected_outputs for task in tasks},
        "proposed_execution_mode": {
            task.title: {
                "executor_type": task.executor_type,
                "tool_refs": task.tool_refs,
                "assigned_model_id": task.assigned_model_id,
            }
            for task in tasks
        },
        "verifier_coverage": {task.title: verifier_strength(task.verifier_refs or []) for task in tasks},
        "high_risk_task_count": len([task for task in tasks if task.risk_level in {"HIGH", "CRITICAL"}]),
        "tasks_requiring_human_approval": [task.title for task in tasks if task.human_review_required],
        "open_questions": plan.open_questions,
        "assumptions": plan.assumptions,
        "policy_warnings": [],
        "recommended_decision": "Approve if the DAG is complete, acyclic, and inside the Task Contract.",
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
    dependency_titles = [
        title
        for (title,) in (
            db.query(models.TaskNode.title)
            .join(models.TaskDependency, models.TaskDependency.from_task_id == models.TaskNode.id)
            .filter(models.TaskDependency.plan_id == task.plan_id, models.TaskDependency.to_task_id == task.id)
            .all()
        )
    ]
    downstream_titles = [
        title
        for (title,) in (
            db.query(models.TaskNode.title)
            .join(models.TaskDependency, models.TaskDependency.to_task_id == models.TaskNode.id)
            .filter(models.TaskDependency.plan_id == task.plan_id, models.TaskDependency.from_task_id == task.id)
            .all()
        )
    ]
    packet = {
        "task_title": task.title,
        "task_description": task.description,
        "why_review_is_required": reason,
        "dependencies": dependency_titles,
        "affected_downstream_tasks": downstream_titles,
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
