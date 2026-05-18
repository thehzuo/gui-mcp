from __future__ import annotations

from sqlalchemy.orm import Session

from app import models
from app.services.state_ledger import write_event


def generate_template_plan(db: Session, run: models.Run) -> models.Plan:
    contract = run.contract
    version = (db.query(models.Plan).filter(models.Plan.run_id == run.id).count() or 0) + 1
    plan = models.Plan(
        run_id=run.id,
        version=version,
        status="DRAFT",
        summary="Template plan generated from the Task Contract for a local MVP execution run.",
        assumptions=[
            "The implementation is local and trusted.",
            "Mock execution is acceptable unless a task is explicitly configured for command execution.",
        ],
        open_questions=[],
    )
    db.add(plan)
    db.flush()

    goal = contract.goal if contract else "Complete the requested mission."
    tasks = [
        models.TaskNode(
            run_id=run.id,
            plan_id=plan.id,
            title="Inspect current mission boundary",
            description=f"Review the Task Contract goal and constraints: {goal}",
            task_family="code_analysis",
            risk_level="LOW",
            reversibility="REVERSIBLE",
            required_autonomy_level="L3",
            expected_outputs=["Mission boundary notes", "Confirmed constraints"],
            verifier_refs=["command_exit_code"],
            tool_refs=["mock_executor"],
            executor_type="mock",
            position_x=0,
            position_y=80,
        ),
        models.TaskNode(
            run_id=run.id,
            plan_id=plan.id,
            title="Design durable state changes",
            description="Map the required durable objects, state transitions, and ledger events.",
            task_family="code_analysis",
            risk_level="MEDIUM",
            reversibility="REVERSIBLE",
            required_autonomy_level="L3",
            expected_outputs=["State model notes", "Transition list"],
            verifier_refs=["command_exit_code"],
            tool_refs=["mock_executor"],
            executor_type="mock",
            position_x=300,
            position_y=0,
        ),
        models.TaskNode(
            run_id=run.id,
            plan_id=plan.id,
            title="Apply implementation change",
            description="Execute the approved implementation task within the Task Contract boundaries.",
            task_family="coding_change",
            risk_level="MEDIUM",
            reversibility="REVERSIBLE",
            required_autonomy_level="L3",
            expected_outputs=["Implemented change", "Execution output"],
            verifier_refs=["command_exit_code"],
            tool_refs=["mock_executor"],
            executor_type="mock",
            position_x=620,
            position_y=80,
        ),
        models.TaskNode(
            run_id=run.id,
            plan_id=plan.id,
            title="Review risky boundary",
            description="Human confirms that the work remains inside the approved mission boundary.",
            task_family="deployment",
            risk_level="HIGH",
            reversibility="PARTIALLY_REVERSIBLE",
            required_autonomy_level="L3",
            expected_outputs=["Human approval decision"],
            verifier_refs=["noop"],
            tool_refs=["mock_executor"],
            executor_type="mock",
            human_review_required=True,
            position_x=620,
            position_y=220,
        ),
        models.TaskNode(
            run_id=run.id,
            plan_id=plan.id,
            title="Verify final result",
            description="Run configured verification and summarize completion status.",
            task_family="coding_change",
            risk_level="LOW",
            reversibility="REVERSIBLE",
            required_autonomy_level="L3",
            expected_outputs=["Verification result", "Final status"],
            verifier_refs=["command_exit_code"],
            tool_refs=["mock_executor"],
            executor_type="mock",
            position_x=940,
            position_y=120,
        ),
    ]
    db.add_all(tasks)
    db.flush()
    deps = [
        models.TaskDependency(plan_id=plan.id, from_task_id=tasks[0].id, to_task_id=tasks[1].id),
        models.TaskDependency(plan_id=plan.id, from_task_id=tasks[1].id, to_task_id=tasks[2].id),
        models.TaskDependency(plan_id=plan.id, from_task_id=tasks[1].id, to_task_id=tasks[3].id),
        models.TaskDependency(plan_id=plan.id, from_task_id=tasks[2].id, to_task_id=tasks[4].id),
        models.TaskDependency(plan_id=plan.id, from_task_id=tasks[3].id, to_task_id=tasks[4].id),
    ]
    db.add_all(deps)
    run.active_plan_id = plan.id
    run.status = "AWAITING_PLAN_REVIEW"
    write_event(
        db,
        run_id=run.id,
        plan_id=plan.id,
        event_type="PLAN_GENERATED",
        payload={"planner": "template", "task_count": len(tasks), "dependency_count": len(deps)},
    )
    return plan

