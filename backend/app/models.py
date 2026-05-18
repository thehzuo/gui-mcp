from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Run(Base, TimestampMixin):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(250))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(64), default="DRAFT", index=True)
    active_plan_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_by: Mapped[str] = mapped_column(String(120), default="local-user")

    contract: Mapped[TaskContract | None] = relationship(back_populates="run", uselist=False, cascade="all, delete-orphan")
    plans: Mapped[list[Plan]] = relationship(back_populates="run", cascade="all, delete-orphan")
    tasks: Mapped[list[TaskNode]] = relationship(back_populates="run", cascade="all, delete-orphan")


class TaskContract(Base, TimestampMixin):
    __tablename__ = "task_contracts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), unique=True, index=True)
    goal: Mapped[str] = mapped_column(Text)
    success_criteria: Mapped[list[str]] = mapped_column(JSON, default=list)
    forbidden_losses: Mapped[list[str]] = mapped_column(JSON, default=list)
    allowed_tools: Mapped[list[str]] = mapped_column(JSON, default=list)
    human_approval_boundaries: Mapped[list[str]] = mapped_column(JSON, default=list)
    risk_class: Mapped[str] = mapped_column(String(32), default="MEDIUM")
    max_autonomy_level: Mapped[str] = mapped_column(String(8), default="L3")
    notes: Mapped[str] = mapped_column(Text, default="")

    run: Mapped[Run] = relationship(back_populates="contract")


class Plan(Base, TimestampMixin):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(64), default="DRAFT", index=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    assumptions: Mapped[list[str]] = mapped_column(JSON, default=list)
    open_questions: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_by: Mapped[str] = mapped_column(String(120), default="template_planner")
    approved_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    run: Mapped[Run] = relationship(back_populates="plans")
    tasks: Mapped[list[TaskNode]] = relationship(back_populates="plan", cascade="all, delete-orphan")
    dependencies: Mapped[list[TaskDependency]] = relationship(back_populates="plan", cascade="all, delete-orphan")


class TaskNode(Base, TimestampMixin):
    __tablename__ = "task_nodes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    plan_id: Mapped[str] = mapped_column(ForeignKey("plans.id"), index=True)
    title: Mapped[str] = mapped_column(String(250))
    description: Mapped[str] = mapped_column(Text, default="")
    task_family: Mapped[str] = mapped_column(String(80), default="general")
    status: Mapped[str] = mapped_column(String(64), default="DRAFT", index=True)
    review_status: Mapped[str] = mapped_column(String(64), default="NOT_REQUIRED", index=True)
    risk_level: Mapped[str] = mapped_column(String(32), default="LOW")
    reversibility: Mapped[str] = mapped_column(String(64), default="REVERSIBLE")
    required_autonomy_level: Mapped[str] = mapped_column(String(8), default="L3")
    assigned_model_id: Mapped[str] = mapped_column(String(120), default="local-default")
    expected_outputs: Mapped[list[str]] = mapped_column(JSON, default=list)
    verifier_refs: Mapped[list[str]] = mapped_column(JSON, default=list)
    tool_refs: Mapped[list[str]] = mapped_column(JSON, default=list)
    executor_type: Mapped[str] = mapped_column(String(64), default="mock")
    executor_config_json: Mapped[dict] = mapped_column(JSON, default=dict)
    human_review_required: Mapped[bool] = mapped_column(Boolean, default=False)
    position_x: Mapped[float] = mapped_column(Float, default=0)
    position_y: Mapped[float] = mapped_column(Float, default=0)

    run: Mapped[Run] = relationship(back_populates="tasks")
    plan: Mapped[Plan] = relationship(back_populates="tasks")


class TaskDependency(Base, TimestampMixin):
    __tablename__ = "task_dependencies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    plan_id: Mapped[str] = mapped_column(ForeignKey("plans.id"), index=True)
    from_task_id: Mapped[str] = mapped_column(ForeignKey("task_nodes.id"), index=True)
    to_task_id: Mapped[str] = mapped_column(ForeignKey("task_nodes.id"), index=True)

    plan: Mapped[Plan] = relationship(back_populates="dependencies")


class StateLedgerEvent(Base):
    __tablename__ = "state_ledger_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    plan_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    task_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(120), index=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    created_by: Mapped[str] = mapped_column(String(120), default="system")


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    task_id: Mapped[str] = mapped_column(ForeignKey("task_nodes.id"), index=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    verifier_name: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(32), index=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ModelCapabilityRecord(Base, TimestampMixin):
    __tablename__ = "model_capability_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    model_id: Mapped[str] = mapped_column(String(120), index=True)
    model_version: Mapped[str] = mapped_column(String(120), default="local")
    task_family: Mapped[str] = mapped_column(String(120), index=True)
    tool_family: Mapped[str] = mapped_column(String(120), default="mock_executor")
    capability_score: Mapped[float] = mapped_column(Float, default=0.6)
    calibration_score: Mapped[float] = mapped_column(Float, default=0.6)
    verified_autonomy_level: Mapped[str] = mapped_column(String(8), default="L3")
    known_failure_modes: Mapped[list[str]] = mapped_column(JSON, default=list)
    required_gates: Mapped[list[str]] = mapped_column(JSON, default=list)
    last_eval_run_id: Mapped[str | None] = mapped_column(String, nullable=True)
    last_evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE")


class ReviewRecord(Base, TimestampMixin):
    __tablename__ = "review_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    plan_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    task_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    review_type: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(64), default="PENDING", index=True)
    reviewer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    decision: Mapped[str | None] = mapped_column(String(64), nullable=True)
    comment: Mapped[str] = mapped_column(Text, default="")
    reason: Mapped[str] = mapped_column(Text, default="")
    packet_json: Mapped[dict] = mapped_column(JSON, default=dict)


class TaskExecution(Base):
    __tablename__ = "task_executions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    task_id: Mapped[str] = mapped_column(ForeignKey("task_nodes.id"), index=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    executor_type: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(64), default="RUNNING", index=True)
    command: Mapped[str | None] = mapped_column(Text, nullable=True)
    stdout: Mapped[str] = mapped_column(Text, default="")
    stderr: Mapped[str] = mapped_column(Text, default="")
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    output_json: Mapped[dict] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

