from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.schemas import DependencyCreate, DependencyRead, TaskNodeCreate, TaskNodeRead, TaskNodeUpdate
from app.services.plan_validator import validate_plan
from app.services.state_ledger import write_event
from app.api.utils import require_editable_plan, require_plan, require_task

router = APIRouter(tags=["tasks"])


@router.post("/api/plans/{plan_id}/tasks", response_model=TaskNodeRead)
def create_task(plan_id: str, payload: TaskNodeCreate, db: Session = Depends(get_db)) -> TaskNodeRead:
    plan = require_plan(db, plan_id)
    require_editable_plan(plan)
    task = models.TaskNode(run_id=plan.run_id, plan_id=plan.id, **payload.model_dump())
    db.add(task)
    db.flush()
    write_event(db, run_id=plan.run_id, plan_id=plan.id, task_id=task.id, event_type="TASK_ADDED", payload=payload.model_dump())
    db.commit()
    db.refresh(task)
    return TaskNodeRead.model_validate(task)


@router.patch("/api/tasks/{task_id}", response_model=TaskNodeRead)
def update_task(task_id: str, payload: TaskNodeUpdate, db: Session = Depends(get_db)) -> TaskNodeRead:
    task = require_task(db, task_id)
    plan = require_plan(db, task.plan_id)
    if plan.status == "LOCKED":
        allowed_after_lock = {"review_status", "status", "position_x", "position_y"}
        if any(key not in allowed_after_lock for key in payload.model_dump(exclude_unset=True)):
            raise HTTPException(status_code=409, detail="Locked plan tasks cannot be structurally edited.")
    else:
        require_editable_plan(plan)
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(task, key, value)
    write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type="TASK_UPDATED", payload=changes)
    db.commit()
    db.refresh(task)
    return TaskNodeRead.model_validate(task)


@router.delete("/api/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    task = require_task(db, task_id)
    plan = require_plan(db, task.plan_id)
    require_editable_plan(plan)
    db.query(models.TaskDependency).filter(
        (models.TaskDependency.from_task_id == task.id) | (models.TaskDependency.to_task_id == task.id)
    ).delete(synchronize_session=False)
    write_event(db, run_id=task.run_id, plan_id=task.plan_id, task_id=task.id, event_type="TASK_UPDATED", payload={"deleted": True})
    db.delete(task)
    db.commit()
    return {"status": "deleted"}


@router.post("/api/plans/{plan_id}/dependencies", response_model=DependencyRead)
def create_dependency(plan_id: str, payload: DependencyCreate, db: Session = Depends(get_db)) -> DependencyRead:
    plan = require_plan(db, plan_id)
    require_editable_plan(plan)
    task_ids = {task.id for task in plan.tasks}
    if payload.from_task_id not in task_ids or payload.to_task_id not in task_ids:
        raise HTTPException(status_code=422, detail="Dependency tasks must belong to the plan.")
    dep = models.TaskDependency(plan_id=plan.id, from_task_id=payload.from_task_id, to_task_id=payload.to_task_id)
    db.add(dep)
    db.flush()
    result = validate_plan(db, plan.id)
    if not result.valid:
        db.rollback()
        raise HTTPException(status_code=422, detail=result.errors)
    write_event(db, run_id=plan.run_id, plan_id=plan.id, event_type="TASK_DEPENDENCY_ADDED", payload=payload.model_dump())
    db.commit()
    db.refresh(dep)
    return DependencyRead.model_validate(dep)


@router.delete("/api/dependencies/{dependency_id}")
def delete_dependency(dependency_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    dep = db.get(models.TaskDependency, dependency_id)
    if not dep:
        raise HTTPException(status_code=404, detail="Dependency not found.")
    plan = require_plan(db, dep.plan_id)
    require_editable_plan(plan)
    write_event(
        db,
        run_id=plan.run_id,
        plan_id=plan.id,
        event_type="TASK_DEPENDENCY_REMOVED",
        payload={"from_task_id": dep.from_task_id, "to_task_id": dep.to_task_id},
    )
    db.delete(dep)
    db.commit()
    return {"status": "deleted"}
