from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.schemas import TaskContractRead, TaskContractUpsert
from app.services.state_ledger import write_event
from app.api.utils import require_run

router = APIRouter(prefix="/api/runs/{run_id}/contract", tags=["contracts"])


@router.get("", response_model=TaskContractRead)
def get_contract(run_id: str, db: Session = Depends(get_db)) -> TaskContractRead:
    run = require_run(db, run_id)
    if not run.contract:
        raise HTTPException(status_code=404, detail="Task Contract not found.")
    return TaskContractRead.model_validate(run.contract)


@router.put("", response_model=TaskContractRead)
def upsert_contract(run_id: str, payload: TaskContractUpsert, db: Session = Depends(get_db)) -> TaskContractRead:
    run = require_run(db, run_id)
    if run.contract:
        contract = run.contract
        for key, value in payload.model_dump().items():
            setattr(contract, key, value)
        event_type = "TASK_CONTRACT_UPDATED"
    else:
        contract = models.TaskContract(run_id=run.id, **payload.model_dump())
        db.add(contract)
        event_type = "TASK_CONTRACT_CREATED"
    if run.status == "DRAFT":
        run.status = "PLANNING"
    write_event(db, run_id=run.id, event_type=event_type, payload=payload.model_dump())
    db.commit()
    db.refresh(contract)
    return TaskContractRead.model_validate(contract)

