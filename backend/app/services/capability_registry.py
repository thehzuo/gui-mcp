from __future__ import annotations

from sqlalchemy.orm import Session

from app import models


DEFAULT_CAPABILITIES = [
    {
        "model_id": "local-default",
        "model_version": "mvp",
        "task_family": "code_analysis",
        "tool_family": "mock_executor",
        "verified_autonomy_level": "L3",
        "capability_score": 0.72,
        "calibration_score": 0.68,
        "required_gates": ["command_exit_code"],
    },
    {
        "model_id": "local-default",
        "model_version": "mvp",
        "task_family": "coding_change",
        "tool_family": "command_executor",
        "verified_autonomy_level": "L3",
        "capability_score": 0.66,
        "calibration_score": 0.62,
        "required_gates": ["command_exit_code"],
        "known_failure_modes": ["may over-edit unrelated files"],
    },
    {
        "model_id": "local-default",
        "model_version": "mvp",
        "task_family": "deployment",
        "tool_family": "command_executor",
        "verified_autonomy_level": "L2",
        "capability_score": 0.4,
        "calibration_score": 0.45,
        "required_gates": ["manual_verifier"],
    },
]


def seed_capabilities(db: Session) -> None:
    if db.query(models.ModelCapabilityRecord).count():
        return
    for item in DEFAULT_CAPABILITIES:
        db.add(models.ModelCapabilityRecord(**item))


def get_capability_for_task(db: Session, task: models.TaskNode) -> models.ModelCapabilityRecord | None:
    tool_family = "command_executor" if task.executor_type == "command" else "mock_executor"
    exact = (
        db.query(models.ModelCapabilityRecord)
        .filter(
            models.ModelCapabilityRecord.model_id == task.assigned_model_id,
            models.ModelCapabilityRecord.task_family == task.task_family,
            models.ModelCapabilityRecord.tool_family == tool_family,
            models.ModelCapabilityRecord.status == "ACTIVE",
        )
        .first()
    )
    if exact:
        return exact
    same_family = (
        db.query(models.ModelCapabilityRecord)
        .filter(
            models.ModelCapabilityRecord.model_id == task.assigned_model_id,
            models.ModelCapabilityRecord.task_family == task.task_family,
            models.ModelCapabilityRecord.status == "ACTIVE",
        )
        .first()
    )
    return same_family
