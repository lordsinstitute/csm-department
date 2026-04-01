"""Pydantic schemas for the VulnScan service — mirrors CognitoForge Labs style."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ScanType(str, Enum):
    FULL     = "full"
    QUICK    = "quick"
    TARGETED = "targeted"


class ScanStatus(str, Enum):
    QUEUED    = "queued"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"


class ScanModule(str, Enum):
    SQL_INJECTION         = "sql_injection"
    XSS                   = "xss"
    CSRF                  = "csrf"
    OPEN_REDIRECT         = "open_redirect"
    PAYMENT_GATEWAY       = "payment_gateway"
    SENSITIVE_DATA        = "sensitive_data_exposure"
    SECURITY_HEADERS      = "security_headers"
    SSL_TLS               = "ssl_tls"
    BROKEN_AUTH           = "broken_auth"
    CORS                  = "cors"
    CLICKJACKING          = "clickjacking"
    SSRF                  = "ssrf"
    XXE                   = "xxe"


# Preset module groups
FULL_SCAN_MODULES  = [m.value for m in ScanModule]
QUICK_SCAN_MODULES = [
    ScanModule.SECURITY_HEADERS.value,
    ScanModule.SSL_TLS.value,
    ScanModule.CORS.value,
    ScanModule.CLICKJACKING.value,
    ScanModule.SENSITIVE_DATA.value,
]


# ---------------------------------------------------------------------------
# Request schema
# ---------------------------------------------------------------------------

class VulnScanRequest(BaseModel):
    """Request payload for a vulnerability scan. Consent is a hard gate."""

    target_url: str
    scan_type: ScanType = ScanType.FULL
    modules: Optional[List[ScanModule]] = None   # None → use scan_type defaults

    # Legal gate — scan is rejected (422) unless True
    consent_confirmed: bool
    requester_name: str
    organization: str
    notes: Optional[str] = None

    @field_validator("consent_confirmed")
    @classmethod
    def must_have_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "Legal consent must be confirmed (consent_confirmed=true) before initiating a scan."
            )
        return v

    @field_validator("target_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("target_url must begin with http:// or https://")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class FindingOut(BaseModel):
    id: str
    scan_id: str
    module: str
    title: str
    severity: str
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    cwe_id: Optional[str] = None
    description: str
    evidence: Optional[str] = None
    affected_url: Optional[str] = None
    parameter: Optional[str] = None
    remediation: str
    reference_links: List[str] = []
    discovered_at: datetime

    model_config = {"from_attributes": True}


class ScanOut(BaseModel):
    id: str
    target_url: str
    scan_type: str
    status: str
    requester_name: str
    organization: str
    modules_requested: List[str]
    modules_completed: List[str]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    findings: List[FindingOut] = []

    model_config = {"from_attributes": True}


class ScanSummary(BaseModel):
    id: str
    target_url: str
    status: str
    scan_type: str
    requester_name: str
    organization: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_findings: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0

    model_config = {"from_attributes": True}


class VulnScanReport(BaseModel):
    """Structured report payload returned by the reports endpoint."""

    scan_id: str
    target_url: str
    organization: str
    requester_name: str
    scan_type: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    risk_score: float
    severity_summary: dict
    priority_findings: List[FindingOut] = []
    all_findings: List[FindingOut] = []
    modules_run: List[str] = []
    gemini_insight: Optional[str] = None