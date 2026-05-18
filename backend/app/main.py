from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import contracts, execution, plans, reviews, runs, stream, tasks
from app.db import SessionLocal, init_db
from app.services.capability_registry import seed_capabilities


app = FastAPI(title="Agent Loom", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs.router)
app.include_router(contracts.router)
app.include_router(plans.router)
app.include_router(tasks.router)
app.include_router(reviews.router)
app.include_router(execution.router)
app.include_router(stream.router)


@app.on_event("startup")
def startup() -> None:
    init_db()
    app.state.scheduler_tasks = {}
    db = SessionLocal()
    try:
        seed_capabilities(db)
        db.commit()
    finally:
        db.close()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

