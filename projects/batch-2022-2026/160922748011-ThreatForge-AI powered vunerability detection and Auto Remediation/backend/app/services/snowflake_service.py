"""Mocked Snowflake data access layer for vulnerability intelligence."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import List

from backend.app.models.schemas import VulnerabilityFinding


@lru_cache
def _load_db() -> List[VulnerabilityFinding]:
    """Load the mock vulnerability database bundled with the application."""

    data_path = Path(__file__).resolve().parents[1] / "data" / "vulnerabilities.json"
    with data_path.open("r", encoding="utf-8") as handle:
        raw_entries = json.load(handle)

    return [VulnerabilityFinding(**entry) for entry in raw_entries]


def find_vulnerabilities_for_repo(repo_id: str) -> List[VulnerabilityFinding]:
    """Return vulnerability records that match the requested repository identifier."""

    # The logic is simplified: we select entries whose repo_ids contain the identifier.
    # Replace this with a Snowflake query once the warehouse is wired into the project.
    findings = [entry for entry in _load_db() if repo_id in entry.affected_components]
    return findings or _load_db()


def list_all_vulnerabilities() -> List[VulnerabilityFinding]:
    """Return every vulnerability record from the mock database."""

    return _load_db()
