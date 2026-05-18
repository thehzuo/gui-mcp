from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import models
from app.db import SessionLocal, get_db
from app.schemas import StateLedgerEventRead
from app.api.utils import require_run

router = APIRouter(tags=["stream"])


@router.get("/api/runs/{run_id}/stream")
def stream_run(run_id: str, db: Session = Depends(get_db)) -> StreamingResponse:
    require_run(db, run_id)

    async def event_generator():
        last_id: str | None = None
        while True:
            poll_db = SessionLocal()
            try:
                query = (
                    poll_db.query(models.StateLedgerEvent)
                    .filter(models.StateLedgerEvent.run_id == run_id)
                    .order_by(models.StateLedgerEvent.created_at.asc())
                )
                events = query.all()
                if last_id:
                    next_events = []
                    seen = False
                    for event in events:
                        if seen:
                            next_events.append(event)
                        elif event.id == last_id:
                            seen = True
                    events = next_events
                for event in events:
                    last_id = event.id
                    payload = StateLedgerEventRead.model_validate(event).model_dump(mode="json")
                    yield f"event: {event.event_type}\nid: {event.id}\ndata: {json.dumps(payload)}\n\n"
            finally:
                poll_db.close()
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

