"""Sandbox simulation helpers for ."""

from __future__ import annotations

from datetime import datetime

from backend.app.models.schemas import AttackPlan


def run_sandbox_simulation(plan: AttackPlan) -> dict[str, object]:
    """Return mock execution logs that would be produced by the containerised sandbox."""

    execution_log = []
    for step in plan.steps:
        execution_log.append(
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "step": step.step_number,
                "action": step.description,
                "status": "success",
            }
        )

    return {
        "repo_id": plan.repo_id,
        "summary": "Simulated attack executed successfully in isolated sandbox.",
        "logs": execution_log,
    }
