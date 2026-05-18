from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import Session

from app import models
from app.schemas import ValidationResult


def validate_plan(db: Session, plan_id: str) -> ValidationResult:
    tasks = db.query(models.TaskNode).filter(models.TaskNode.plan_id == plan_id).all()
    dependencies = db.query(models.TaskDependency).filter(models.TaskDependency.plan_id == plan_id).all()
    task_ids = {task.id for task in tasks}
    errors: list[str] = []
    warnings: list[str] = []

    if not tasks:
        errors.append("Plan must contain at least one task.")

    for task in tasks:
        if not task.title.strip():
            errors.append(f"Task {task.id} is missing a title.")
        if not task.description.strip():
            errors.append(f"Task {task.title} is missing a description.")
        if not task.expected_outputs:
            errors.append(f"Task {task.title} must declare expected outputs.")
        if not task.risk_level:
            errors.append(f"Task {task.title} must declare risk level.")
        if not task.reversibility:
            errors.append(f"Task {task.title} must declare reversibility.")
        if not task.verifier_refs:
            warnings.append(f"Task {task.title} has no verifier references.")

    graph: dict[str, list[str]] = defaultdict(list)
    for dep in dependencies:
        if dep.from_task_id not in task_ids:
            errors.append(f"Dependency {dep.id} references missing from_task_id {dep.from_task_id}.")
        if dep.to_task_id not in task_ids:
            errors.append(f"Dependency {dep.id} references missing to_task_id {dep.to_task_id}.")
        if dep.from_task_id == dep.to_task_id:
            errors.append("A task cannot depend on itself.")
        graph[dep.from_task_id].append(dep.to_task_id)

    if _has_cycle(task_ids, graph):
        errors.append("Dependency graph contains a cycle.")

    return ValidationResult(valid=not errors, errors=errors, warnings=warnings)


def _has_cycle(task_ids: set[str], graph: dict[str, list[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> bool:
        if node_id in visiting:
            return True
        if node_id in visited:
            return False
        visiting.add(node_id)
        for next_id in graph.get(node_id, []):
            if visit(next_id):
                return True
        visiting.remove(node_id)
        visited.add(node_id)
        return False

    return any(visit(task_id) for task_id in task_ids)

