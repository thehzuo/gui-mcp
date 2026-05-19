from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


AutonomyLevel = Literal["L0", "L1", "L2", "L3", "L4", "L5"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
Reversibility = Literal["REVERSIBLE", "PARTIALLY_REVERSIBLE", "IRREVERSIBLE"]


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RunCreate(BaseModel):
    name: str
    description: str = ""


class RunUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RunRead(APIModel):
    id: str
    name: str
    description: str
    status: str
    active_plan_id: str | None
    created_by: str
    created_at: datetime
    updated_at: datetime
    progress_summary: dict[str, int] = Field(default_factory=dict)


class TaskContractUpsert(BaseModel):
    goal: str
    success_criteria: list[str] = Field(default_factory=list)
    forbidden_losses: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=lambda: ["mock_executor", "command_executor", "test_runner"])
    human_approval_boundaries: list[str] = Field(default_factory=lambda: ["before_plan_execution", "before_irreversible_action"])
    risk_class: str = "MEDIUM"
    max_autonomy_level: AutonomyLevel = "L3"
    notes: str = ""


class TaskContractRead(TaskContractUpsert, APIModel):
    id: str
    run_id: str
    created_at: datetime
    updated_at: datetime


class TaskNodeBase(BaseModel):
    title: str
    description: str = ""
    task_family: str = "general"
    risk_level: RiskLevel = "LOW"
    reversibility: Reversibility = "REVERSIBLE"
    required_autonomy_level: AutonomyLevel = "L3"
    assigned_model_id: str = "local-default"
    expected_outputs: list[str] = Field(default_factory=list)
    verifier_refs: list[str] = Field(default_factory=lambda: ["command_exit_code"])
    tool_refs: list[str] = Field(default_factory=lambda: ["mock_executor"])
    executor_type: Literal["mock", "command"] = "mock"
    executor_config_json: dict[str, Any] = Field(default_factory=dict)
    human_review_required: bool = False
    position_x: float = 0
    position_y: float = 0


class TaskNodeCreate(TaskNodeBase):
    pass


class TaskNodeUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    task_family: str | None = None
    status: str | None = None
    review_status: str | None = None
    risk_level: RiskLevel | None = None
    reversibility: Reversibility | None = None
    required_autonomy_level: AutonomyLevel | None = None
    assigned_model_id: str | None = None
    expected_outputs: list[str] | None = None
    verifier_refs: list[str] | None = None
    tool_refs: list[str] | None = None
    executor_type: Literal["mock", "command"] | None = None
    executor_config_json: dict[str, Any] | None = None
    human_review_required: bool | None = None
    position_x: float | None = None
    position_y: float | None = None


class TaskNodeRead(TaskNodeBase, APIModel):
    id: str
    run_id: str
    plan_id: str
    status: str
    review_status: str
    created_at: datetime
    updated_at: datetime


class DependencyCreate(BaseModel):
    from_task_id: str
    to_task_id: str


class DependencyRead(APIModel):
    id: str
    plan_id: str
    from_task_id: str
    to_task_id: str
    created_at: datetime


class PlanRead(APIModel):
    id: str
    run_id: str
    version: int
    status: str
    summary: str
    assumptions: list[str]
    open_questions: list[str]
    created_by: str
    approved_by: str | None
    approved_at: datetime | None
    locked_at: datetime | None
    created_at: datetime
    updated_at: datetime
    tasks: list[TaskNodeRead] = Field(default_factory=list)
    dependencies: list[DependencyRead] = Field(default_factory=list)


class PlanPatch(BaseModel):
    summary: str | None = None
    assumptions: list[str] | None = None
    open_questions: list[str] | None = None


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class StateLedgerEventRead(APIModel):
    id: str
    run_id: str
    plan_id: str | None
    task_id: str | None
    event_type: str
    payload_json: dict[str, Any]
    created_at: datetime
    created_by: str


class VerificationResultRead(APIModel):
    id: str
    task_id: str
    run_id: str
    verifier_name: str
    status: str
    score: float | None
    summary: str
    evidence_json: dict[str, Any]
    created_at: datetime


class ReviewRead(APIModel):
    id: str
    run_id: str
    plan_id: str | None
    task_id: str | None
    review_type: str
    status: str
    reviewer: str | None
    decision: str | None
    comment: str
    reason: str
    packet_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ReviewDecision(BaseModel):
    reviewer: str = "local-reviewer"
    comment: str = ""


class TaskExecutionRead(APIModel):
    id: str
    task_id: str
    run_id: str
    executor_type: str
    status: str
    command: str | None
    stdout: str
    stderr: str
    exit_code: int | None
    duration_ms: int
    output_json: dict[str, Any]
    started_at: datetime
    finished_at: datetime | None


class PolicyDecisionRead(BaseModel):
    decision: Literal["AUTO_EXECUTE", "DRY_RUN_REQUIRED", "HUMAN_REVIEW_REQUIRED", "BLOCKED"]
    reason: str
    required_action: str


class RunStatusRead(BaseModel):
    run: RunRead
    plan: PlanRead | None
    reviews: list[ReviewRead]
    verification_results: list[VerificationResultRead]
    events: list[StateLedgerEventRead]
    task_executions: list[TaskExecutionRead] = Field(default_factory=list)
    blocked_reasons: dict[str, str] = Field(default_factory=dict)
    review_reasons: dict[str, str] = Field(default_factory=dict)
    policy_summaries: dict[str, PolicyDecisionRead] = Field(default_factory=dict)
