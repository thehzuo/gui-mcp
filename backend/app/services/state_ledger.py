from __future__ import annotations

from sqlalchemy.orm import Session

from app import models


def write_event(
    db: Session,
    *,
    run_id: str,
    event_type: str,
    plan_id: str | None = None,
    task_id: str | None = None,
    payload: dict | None = None,
    created_by: str = "system",
) -> models.StateLedgerEvent:
    event = models.StateLedgerEvent(
        run_id=run_id,
        plan_id=plan_id,
        task_id=task_id,
        event_type=event_type,
        payload_json=payload or {},
        created_by=created_by,
    )
    db.add(event)
    return event

