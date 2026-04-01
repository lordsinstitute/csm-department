"""File-system helpers for simulation artefacts."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List

from pydantic import ValidationError

from backend.app.models.schemas import SimulationRun, SimulationSummary

logger = logging.getLogger(__name__)

_SIMULATIONS_DIR = Path(__file__).resolve().parents[1] / "data" / "simulations"


class SimulationDataError(RuntimeError):
    """Raised when simulation data cannot be read or parsed."""


class SimulationNotFoundError(FileNotFoundError):
    """Raised when a specific simulation run cannot be located."""


def ensure_simulation_dir() -> Path:
    """Ensure the simulations directory exists and return its path."""

    _SIMULATIONS_DIR.mkdir(parents=True, exist_ok=True)
    return _SIMULATIONS_DIR


def _load_raw_json(file_path: Path) -> dict:
    """Load raw JSON from disk with consistent error handling."""

    try:
        with file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        logger.exception("Failed to read simulation file %s", file_path, exc_info=exc)
        raise SimulationDataError("Simulation data corrupted or missing") from exc


def list_simulations(repo_id: str) -> List[SimulationSummary]:
    """Return summaries for all simulation runs associated with the repository."""

    directory = ensure_simulation_dir()
    summaries: List[SimulationSummary] = []
    for file_path in directory.glob(f"{repo_id}_*.json"):
        raw_data = _load_raw_json(file_path)
        try:
            run = SimulationRun(**raw_data)
        except ValidationError as exc:
            logger.exception("Failed to validate simulation payload from %s", file_path, exc_info=exc)
            raise SimulationDataError("Simulation data corrupted or missing") from exc

        summaries.append(
            SimulationSummary(repo_id=run.repo_id, run_id=run.run_id, timestamp=run.timestamp)
        )

    summaries.sort(key=lambda item: item.timestamp, reverse=True)
    return summaries


def load_simulation(repo_id: str, run_id: str) -> SimulationRun:
    """Load a persisted simulation run ensuring it belongs to the requested repo."""

    directory = ensure_simulation_dir()
    file_path = directory / f"{run_id}.json"
    if not file_path.exists():
        raise SimulationNotFoundError(
            f"Simulation run '{run_id}' not found for repository '{repo_id}'"
        )

    raw_data = _load_raw_json(file_path)
    try:
        run = SimulationRun(**raw_data)
    except ValidationError as exc:
        logger.exception("Failed to validate simulation payload from %s", file_path, exc_info=exc)
        raise SimulationDataError("Simulation data corrupted or missing") from exc

    if run.repo_id != repo_id:
        raise SimulationNotFoundError(
            f"Simulation run '{run_id}' is not associated with repository '{repo_id}'"
        )

    return run
