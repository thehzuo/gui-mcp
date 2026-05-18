from app import models
from app.db import SessionLocal
from tests.helpers import create_run_with_contract


def test_run_contract_plan_and_ledger_survive_new_session(client):
    run = create_run_with_contract(client)
    plan = client.post(f"/api/runs/{run['id']}/plans/generate").json()
    client.post(f"/api/plans/{plan['id']}/submit-review")

    db = SessionLocal()
    try:
        persisted_run = db.get(models.Run, run["id"])
        persisted_plan = db.get(models.Plan, plan["id"])
        events = db.query(models.StateLedgerEvent).filter(models.StateLedgerEvent.run_id == run["id"]).all()

        assert persisted_run is not None
        assert persisted_run.contract.goal == "Build a DAG execution flow."
        assert persisted_plan is not None
        assert len(persisted_plan.tasks) == 5
        assert len(persisted_plan.dependencies) == 5
        assert [event.event_type for event in events][:2] == ["RUN_CREATED", "TASK_CONTRACT_CREATED"]
    finally:
        db.close()


def test_ledger_events_are_append_only_for_mutations(client):
    run = create_run_with_contract(client)
    first_count = len(client.get(f"/api/runs/{run['id']}/events").json())

    client.patch(f"/api/runs/{run['id']}", json={"description": "changed once"})
    second_count = len(client.get(f"/api/runs/{run['id']}/events").json())

    client.patch(f"/api/runs/{run['id']}", json={"description": "changed twice"})
    third_count = len(client.get(f"/api/runs/{run['id']}/events").json())

    assert second_count == first_count + 1
    assert third_count == second_count + 1
