"""
VulnScan internal data models.
Dataclasses mirror the PostgreSQL tables defined in migration_vulnscan.sql.
Column names and types match 1-to-1 so db.py can INSERT/SELECT without remapping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


# ---------------------------------------------------------------------------
# VulnFinding — mirrors: vulnscan_findings
# ---------------------------------------------------------------------------

@dataclass
class VulnFinding:
    """
    A single vulnerability finding produced by a scanner module.

    DB-generated (do NOT set manually):
        id           TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text
        scan_id      TEXT NOT NULL REFERENCES vulnscan_scans(id) ON DELETE CASCADE
        discovered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

    NOT NULL columns (must be set by scanner):
        module, title, severity, description, remediation

    Nullable columns:
        cvss_score, cve_id, cwe_id, evidence, affected_url, parameter

    JSONB column (NOT NULL DEFAULT '[]'):
        references  → List[str] in Python
    """

    # NOT NULL — required by every scanner module
    module: str           # e.g. "xss", "sql_injection", "cors"
    title: str            # short human-readable title
    severity: str         # INFO | LOW | MEDIUM | HIGH | CRITICAL
    description: str      # full description of the finding
    remediation: str      # actionable fix guidance

    # JSONB NOT NULL DEFAULT '[]'
    reference_links: List[str] = field(default_factory=list)

    # Nullable
    cvss_score: Optional[float] = None   # NUMERIC(4,1) e.g. 7.5
    cve_id: Optional[str] = None         # e.g. "CVE-2023-12345"
    cwe_id: Optional[str] = None         # e.g. "CWE-79"
    evidence: Optional[str] = None       # raw response snippet / proof
    affected_url: Optional[str] = None   # specific URL where finding was observed
    parameter: Optional[str] = None      # query param or form field name if applicable


# ---------------------------------------------------------------------------
# ScanRecord — mirrors: vulnscan_scans
# ---------------------------------------------------------------------------

@dataclass
class ScanRecord:
    """
    Represents a row in vulnscan_scans.
    Used when reading scan state back from the DB (status polling, report building).

    DB-generated (do NOT set manually on INSERT):
        id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text
        created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()

    NOT NULL columns:
        target_url, scan_type, status, consent_confirmed,
        requester_name, organization,
        modules_requested, modules_completed

    Nullable columns:
        notes, started_at, completed_at, error_message
    """

    # NOT NULL
    target_url: str
    scan_type: str            # full | quick | targeted
    status: str               # queued | running | completed | failed
    consent_confirmed: bool
    requester_name: str
    organization: str

    # JSONB NOT NULL DEFAULT '[]'
    modules_requested: List[str] = field(default_factory=list)
    modules_completed: List[str] = field(default_factory=list)

    # Set after INSERT or when reading from DB
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    # Nullable
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None