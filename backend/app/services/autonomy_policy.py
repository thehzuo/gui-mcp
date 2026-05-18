from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app import models
from app.services.capability_registry import get_capability_for_task
from app.services.verifier import verifier_strength


AUTONOMY_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}


@dataclass
class PolicyDecision:
    decision: str
    reason: str
    required_action: str


def autonomy_gte(left: str, right: str) -> bool:
    return AUTONOMY_ORDER.get(left, -1) >= AUTONOMY_ORDER.get(right, 99)


def decide_task_execution(
    db: Session,
    *,
    task: models.TaskNode,
    plan: models.Plan,
    contract: models.TaskContract | None,
) -> PolicyDecision:
    if plan.status != "LOCKED":
        return PolicyDecision("BLOCKED", "Plan is not approved and locked.", "Approve and lock the plan.")
    if not contract:
        return PolicyDecision("BLOCKED", "Run has no Task Contract.", "Create a Task Contract.")

    if task.executor_type == "command":
        used_tools = set(task.tool_refs or ["command_executor"])
    else:
        used_tools = set(task.tool_refs or ["mock_executor"])
    allowed_tools = set(contract.allowed_tools or [])
    if not used_tools.issubset(allowed_tools):
        return PolicyDecision(
            "BLOCKED",
            f"Task uses tools outside the Task Contract: {sorted(used_tools - allowed_tools)}.",
            "Edit the task tools or update the Task Contract.",
        )

    if task.review_status == "PENDING":
        return PolicyDecision("BLOCKED", "Task has a pending human review.", "Approve or reject the review.")
    if task.human_review_required and task.review_status != "APPROVED":
        return PolicyDecision("HUMAN_REVIEW_REQUIRED", "Task is explicitly marked for human review.", "Approve or edit the task.")
    if task.risk_level == "CRITICAL" and task.review_status != "APPROVED":
        return PolicyDecision("HUMAN_REVIEW_REQUIRED", "Task risk is CRITICAL.", "Approve, reject, or edit the task.")
    if task.reversibility == "IRREVERSIBLE" and task.review_status != "APPROVED":
        return PolicyDecision("HUMAN_REVIEW_REQUIRED", "Task is irreversible.", "Approve, reject, or edit the task.")

    strength = verifier_strength(task.verifier_refs or [])
    if task.risk_level == "HIGH" and strength in {"NONE", "WEAK"} and task.review_status != "APPROVED":
        return PolicyDecision(
            "HUMAN_REVIEW_REQUIRED",
            f"Task is high risk and verifier strength is {strength}.",
            "Approve, reject, or add a stronger verifier.",
        )

    if not autonomy_gte(contract.max_autonomy_level, task.required_autonomy_level) and task.review_status != "APPROVED":
        return PolicyDecision(
            "HUMAN_REVIEW_REQUIRED",
            "Task requires a higher autonomy level than the Task Contract allows.",
            "Approve the task manually or reduce required autonomy.",
        )

    capability = get_capability_for_task(db, task)
    if capability and not autonomy_gte(capability.verified_autonomy_level, task.required_autonomy_level) and task.review_status != "APPROVED":
        return PolicyDecision(
            "HUMAN_REVIEW_REQUIRED",
            "Assigned model capability is below the task autonomy requirement.",
            "Approve the task manually or assign a more capable model.",
        )
    if not capability and task.required_autonomy_level not in {"L0", "L1", "L2"} and task.review_status != "APPROVED":
        return PolicyDecision(
            "HUMAN_REVIEW_REQUIRED",
            "No active capability registry record covers this task.",
            "Approve manually or add a capability record.",
        )

    return PolicyDecision("AUTO_EXECUTE", "Dependencies satisfied and policy allows execution.", "Queue the task.")
