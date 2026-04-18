"""Simulated DigitalOcean Gradient integration for CognitoForge Labs."""

from __future__ import annotations

import json
import logging
import os
import random
import time
from typing import Any, Dict

# Allow running as a standalone script by ensuring repository root is on sys.path.
if __package__ in {None, ""}:
    import pathlib
    import sys

    current_file = pathlib.Path(__file__).resolve()
    repo_root = current_file.parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    package_root = current_file.parents[1]
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))

from backend.app.services.gemini_service import generate_ai_insight

logger = logging.getLogger(__name__)


def _should_use_mock() -> bool:
    """Return True unless USE_GRADIENT_MOCK is explicitly set to 'false'."""

    return os.getenv("USE_GRADIENT_MOCK", "true").strip().lower() != "false"


def init_gradient() -> bool:
    """Simulate initialising a DigitalOcean Gradient cluster."""

    if not _should_use_mock():
        message = "Real Gradient API integration not available — running mock mode instead."
        print(message)
        logger.warning(message)

    logger.info("Connecting to DigitalOcean Gradient...")
    # Simulate connection latency without blocking for too long.
    time.sleep(0.1)
    logger.info("Gradient cluster initialized successfully (mock mode).")
    return True


def _invoke_gemini(payload: Dict[str, Any]) -> str:
    """Attempt to produce an insight via the existing Gemini integration."""

    try:
        insight = generate_ai_insight(payload)  # type: ignore[arg-type]
        if insight:
            return str(insight)
    except TypeError as exc:
        logger.debug("Gemini insight invocation failed", extra={"error": str(exc)})
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error while generating Gemini insight", extra={"error": str(exc)})
    return "Simulated Gemini insight unavailable"


def run_gradient_task(task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate executing an AI task on Gradient, optionally delegating to Gemini."""

    logger.info("Running Gradient task", extra={"task": task_name})
    start = time.perf_counter()

    try:
        time.sleep(random.uniform(0.5, 2.0))

        output = "Simulated Gradient task output"
        if task_name == "ai_insight":
            output = _invoke_gemini(payload)

        execution_time = time.perf_counter() - start
        response = {
            "status": "success",
            "task": task_name,
            "output": output,
            "metadata": {
                "runtime_env": "DigitalOcean Gradient (Simulated)",
                "instance_type": "g1-small (mock)",
                "execution_time": round(execution_time, 3),
            },
        }

        logger.info("Gradient task completed", extra={"task": task_name, "execution_time": execution_time})
        return response
    except Exception as exc:  # noqa: BLE001
        logger.exception("Gradient task failed", extra={"task": task_name, "error": str(exc)})
        return {
            "status": "error",
            "task": task_name,
            "output": "Gradient task encountered an unexpected error",
            "metadata": {
                "runtime_env": "DigitalOcean Gradient (Simulated)",
                "instance_type": "g1-small (mock)",
                "execution_time": round(time.perf_counter() - start, 3),
            },
        }


def get_gradient_status() -> Dict[str, Any]:
    """Return a mock cluster status payload."""

    return {
        "connected": True,
        "mock_mode": True,
        "message": "Connected to DigitalOcean Gradient (Simulated Mode)",
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_gradient()
    result = run_gradient_task("ai_insight", {"repo_id": "demo-repo", "summary": "mock analysis"})
    print(json.dumps(result, indent=2))
