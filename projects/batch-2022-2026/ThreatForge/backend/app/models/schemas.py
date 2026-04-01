"""Pydantic schemas shared across the CognitoForge Labs backend."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class RepoUpload(BaseModel):
    """Payload describing a repository that should be ingested by the platform."""

    repo_id: str = Field(..., description="Unique handle applied to the uploaded repository.")
    repo_url: Optional[HttpUrl] = Field(
        default=None,
        description="Git-hosted repository URL when the user prefers remote ingestion.",
    )
    zip_file_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded archive when the upload happens through the UI.",
    )
    metadata: dict[str, str] = Field(
        default_factory=dict,
        description="Free-form metadata that can tag the ingestion request for later lookup.",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "repo_id": "demo-repo",
                    "repo_url": "https://github.com/example/demo",
                },
                {
                    "repo_id": "uploaded-repo",
                    "zip_file_base64": "UEsDBBQAAAAIANJ...",
                },
            ]
        }
    }


class AttackStep(BaseModel):
    """Single step of a simulated adversarial campaign."""

    step_number: int = Field(..., ge=1, description="Ordinal of the attack step within the scenario.")
    description: str = Field(..., description="Readable explanation of the adversarial action.")
    technique_id: str = Field(..., description="MITRE ATT&CK technique identifier used in the step.")
    severity: str = Field(..., description="Severity grading for this individual step.")
    affected_files: List[str] = Field(
        default_factory=list,
        description="Repository files that the simulated action touched.",
    )


class AttackPlan(BaseModel):
    """Composite attack plan returned by the AI planning phase."""

    repo_id: str = Field(..., description="Identifier previously registered for the repository.")
    overall_severity: str = Field(..., description="Aggregate severity rating for the full plan.")
    steps: List[AttackStep] = Field(
        default_factory=list,
        description="Ordered sequence outlining the simulated adversarial flow.",
    )


class VulnerabilityFinding(BaseModel):
    """Single vulnerability entry enriched with TTP mapping and remediation advice."""

    cve_id: str = Field(..., description="CVE identifier associated with the finding.")
    ttp: str = Field(..., description="Associated MITRE ATT&CK tactic or technique.")
    remediation: str = Field(..., description="Recommended fix or mitigation guidance.")
    affected_components: List[str] = Field(
        default_factory=list,
        description="List of code artifacts involved in the finding.",
    )


class VulnerabilityReport(BaseModel):
    """Aggregated vulnerability report for a repository under test."""

    repo_id: str = Field(..., description="Repository identifier used to generate the report.")
    findings: List[VulnerabilityFinding] = Field(
        default_factory=list,
        description="Collection of vulnerability findings discovered during analysis.",
    )


class SimulationSummary(BaseModel):
    """Lightweight view of a saved simulation run."""

    repo_id: str = Field(..., description="Repository identifier that generated the run.")
    run_id: str = Field(..., description="Unique identifier derived from repo and timestamp.")
    timestamp: datetime = Field(..., description="UTC timestamp when the run was persisted.")


class SimulationRun(SimulationSummary):
    """Full persisted simulation payload combining plan and sandbox results."""

    plan: AttackPlan = Field(..., description="Attack plan produced for the simulation run.")
    sandbox: Dict[str, Any] = Field(
        default_factory=dict,
        description="Sandbox execution artefacts captured for the run.",
    )


class SimulationReport(BaseModel):
    """Structured breakdown of a simulation run for reporting endpoints."""

    repo_id: str = Field(..., description="Repository identifier for the report.")
    run_id: str = Field(..., description="Simulation run identifier being summarised.")
    summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key metrics and affected artefacts extracted from the run.",
    )
    ai_insight: Optional[str] = Field(
        default=None,
        description="Short AI-generated summary produced by Gemini when available.",
    )
