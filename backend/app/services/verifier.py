from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app import models


VERIFIER_STRENGTH = {
    "noop": "NONE",
    "manual_verifier": "MEDIUM",
    "manual_summary_review": "MEDIUM",
    "command_exit_code": "MEDIUM",
    "unit_tests": "STRONG",
}


@dataclass
class VerificationOutcome:
    verifier_name: str
    status: str
    summary: str
    score: float | None = None
    evidence: dict | None = None


def verifier_strength(verifier_refs: list[str]) -> str:
    if not verifier_refs:
        return "NONE"
    order = {"NONE": 0, "WEAK": 1, "MEDIUM": 2, "STRONG": 3}
    strongest = "NONE"
    for ref in verifier_refs:
        strength = VERIFIER_STRENGTH.get(ref, "WEAK")
        if order[strength] > order[strongest]:
            strongest = strength
    return strongest


def verify_task(db: Session, task: models.TaskNode, execution: models.TaskExecution) -> list[models.VerificationResult]:
    refs = task.verifier_refs or ["noop"]
    results: list[models.VerificationResult] = []
    for ref in refs:
        outcome = _verify(ref, execution)
        result = models.VerificationResult(
            task_id=task.id,
            run_id=task.run_id,
            verifier_name=outcome.verifier_name,
            status=outcome.status,
            score=outcome.score,
            summary=outcome.summary,
            evidence_json=outcome.evidence or {},
        )
        db.add(result)
        results.append(result)
    return results


def _verify(ref: str, execution: models.TaskExecution) -> VerificationOutcome:
    if ref in {"command_exit_code", "unit_tests"}:
        passed = execution.exit_code == 0
        return VerificationOutcome(
            verifier_name=ref,
            status="PASS" if passed else "FAIL",
            summary="Command completed with exit code 0." if passed else f"Command failed with exit code {execution.exit_code}.",
            score=1.0 if passed else 0.0,
            evidence={"exit_code": execution.exit_code, "duration_ms": execution.duration_ms},
        )
    if ref in {"manual_verifier", "manual_summary_review"}:
        return VerificationOutcome(
            verifier_name=ref,
            status="UNKNOWN",
            summary="Manual verification is required before this task can be considered complete.",
            evidence={"requires_human": True},
        )
    return VerificationOutcome(
        verifier_name=ref or "noop",
        status="UNKNOWN",
        summary="No deterministic verifier was configured.",
    )

