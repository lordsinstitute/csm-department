"""
VulnScan API router — passive web vulnerability detection service.
Follows the CognitoForge Labs router conventions established in operations.py,
performance.py and ai.py.

Endpoints:
    POST   /api/vulnscan/scans              — queue a new scan
    GET    /api/vulnscan/scans              — list all scans
    GET    /api/vulnscan/scans/{scan_id}    — get scan + findings
    DELETE /api/vulnscan/scans/{scan_id}    — delete a scan (not running)
    GET    /api/vulnscan/scans/{scan_id}/findings  — filtered findings
    GET    /api/vulnscan/modules            — list available modules
    GET    /api/vulnscan/reports/{scan_id}  — full JSON report
    GET    /api/vulnscan/analytics          — aggregate stats
"""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from fastapi.concurrency import run_in_threadpool

from backend.app.services.vulnscan import db as vulnscan_db
from backend.app.services.vulnscan.scanner import run_scan, _resolve_modules
from backend.app.services.vulnscan.schemas import (
    VulnScanRequest,
    ScanSummary,
    ScanOut,
    FindingOut,
    VulnScanReport,
    ScanModule,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vulnscan", tags=["vulnscan"])


# ---------------------------------------------------------------------------
# Module listing
# ---------------------------------------------------------------------------

_MODULE_DESCRIPTIONS = {
    "security_headers":      "Checks for 9 required HTTP security headers and flags dangerous ones.",
    "ssl_tls":               "Inspects TLS certificate expiry, self-signed certs, weak protocols and ciphers.",
    "sql_injection":         "Error-based SQL injection detection on URL parameters and HTML forms.",
    "xss":                   "Reflected XSS probe and DOM sink detection.",
    "payment_gateway":       "PCI-DSS checks, card number patterns, leaked Stripe/PayPal/AWS keys.",
    "sensitive_data_exposure": "30+ path probes for .env, .git, SQL dumps and secret files.",
    "cors":                  "Wildcard and reflected-origin CORS misconfiguration checks.",
    "csrf":                  "POST form CSRF token absence detection.",
    "open_redirect":         "Open redirect parameter probing.",
    "clickjacking":          "X-Frame-Options and CSP frame-ancestors absence checks.",
    "broken_auth":           "Session cookie flag analysis (Secure, HttpOnly, SameSite).",
    "ssrf":                  "SSRF-prone parameter name detection.",
    "xxe":                   "XML endpoint OPTIONS detection.",
}


@router.get("/modules")
async def list_modules() -> dict:
    """List all available scanner modules with descriptions."""
    return {
        "modules": [
            {
                "name": m.value,
                "description": _MODULE_DESCRIPTIONS.get(m.value, ""),
            }
            for m in ScanModule
        ]
    }


# ---------------------------------------------------------------------------
# Scan CRUD
# ---------------------------------------------------------------------------

@router.post("/scans", status_code=202)
async def create_scan(
    payload: VulnScanRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Queue a new vulnerability scan.

    Consent gate: `consent_confirmed` must be `true` or the request is rejected
    with HTTP 422. Scans run asynchronously — poll the scan status endpoint.

    **Example:**
    ```json
    {
        "target_url": "https://example.com",
        "scan_type": "full",
        "consent_confirmed": true,
        "requester_name": "Alice Smith",
        "organization": "Acme Corp"
    }
    ```
    """
    logger.info(
        "VulnScan scan requested",
        extra={
            "target": payload.target_url,
            "type": payload.scan_type,
            "org": payload.organization,
        },
    )

    modules = _resolve_modules(
        payload.scan_type.value,
        [m.value for m in payload.modules] if payload.modules else None,
    )

    try:
        scan_id = await run_in_threadpool(
            vulnscan_db.create_scan,
            payload.target_url,
            payload.scan_type.value,
            modules,
            payload.requester_name,
            payload.organization,
            payload.notes,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={"error": str(exc)}) from exc

    background_tasks.add_task(
        run_scan,
        scan_id,
        payload.target_url,
        payload.scan_type.value,
        modules,
    )

    logger.info("VulnScan queued", extra={"scan_id": scan_id})
    return {
        "scan_id": scan_id,
        "status": "queued",
        "target_url": payload.target_url,
        "modules": modules,
        "message": f"Scan queued. Poll GET /api/vulnscan/scans/{scan_id} for status.",
    }


@router.get("/scans")
async def list_scans(
    status: Optional[str] = Query(None, description="Filter by status: queued|running|completed|failed"),
    limit: int = Query(50, ge=1, le=200),
) -> dict:
    """List vulnerability scans with severity summary counts."""
    try:
        scans = await run_in_threadpool(vulnscan_db.list_scans, limit, status)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={"error": str(exc)}) from exc

    return {"total": len(scans), "scans": scans}


@router.get("/scans/{scan_id}")
async def get_scan(scan_id: str) -> dict:
    """Retrieve full scan record including all findings."""
    try:
        scan = await run_in_threadpool(vulnscan_db.get_scan, scan_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={"error": str(exc)}) from exc

    if not scan:
        raise HTTPException(status_code=404, detail={"error": f"Scan '{scan_id}' not found."})

    findings = await run_in_threadpool(vulnscan_db.get_findings, scan_id)
    scan["findings"] = findings
    return scan


@router.delete("/scans/{scan_id}", status_code=204)
async def delete_scan(scan_id: str) -> None:
    """Delete a scan and its findings. Returns 409 if the scan is still running."""
    try:
        scan = await run_in_threadpool(vulnscan_db.get_scan, scan_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={"error": str(exc)}) from exc

    if not scan:
        raise HTTPException(status_code=404, detail={"error": f"Scan '{scan_id}' not found."})

    if scan["status"] == "running":
        raise HTTPException(
            status_code=409,
            detail={"error": "Cannot delete a running scan. Wait for completion or restart the service."},
        )

    conn = vulnscan_db._get_conn()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM vulnscan_scans WHERE id = %s", (scan_id,))


@router.get("/scans/{scan_id}/findings")
async def get_findings(
    scan_id: str,
    severity: Optional[str] = Query(None, description="CRITICAL|HIGH|MEDIUM|LOW|INFO"),
    module: Optional[str] = Query(None, description="e.g. xss, sql_injection"),
) -> dict:
    """Return findings for a scan, optionally filtered by severity or module."""
    try:
        findings = await run_in_threadpool(
            vulnscan_db.get_findings, scan_id, severity, module
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={"error": str(exc)}) from exc

    return {"scan_id": scan_id, "total": len(findings), "findings": findings}


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

@router.get("/reports/{scan_id}")
async def get_report(scan_id: str) -> dict:
    """
    Return a structured vulnerability report for a completed scan.

    Includes risk score (0–10), severity summary, and top priority findings.
    If Gemini is enabled (USE_GEMINI=true), an AI-generated insight is appended.
    """
    try:
        report = await run_in_threadpool(vulnscan_db.build_report, scan_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={"error": str(exc)}) from exc

    if not report:
        raise HTTPException(status_code=404, detail={"error": f"Scan '{scan_id}' not found."})

    scan = await run_in_threadpool(vulnscan_db.get_scan, scan_id)
    if scan and scan["status"] != "completed":
        raise HTTPException(
            status_code=409,
            detail={"error": f"Scan is still '{scan['status']}'. Report available after completion."},
        )

    # Optionally enrich with Gemini insight
    try:
        from backend.app.core.settings import get_settings
        from backend.app.services.gemini_service import generate_gemini_response
        from fastapi.concurrency import run_in_threadpool as rtp

        settings = get_settings()
        if settings.use_gemini and settings.gemini_api_key:
            sev = report["severity_summary"]
            top_titles = [f["title"] for f in report["priority_findings"][:3]]
            prompt = (
                f"Security scan of {report['target_url']} found: "
                f"CRITICAL={sev.get('CRITICAL',0)}, HIGH={sev.get('HIGH',0)}, "
                f"MEDIUM={sev.get('MEDIUM',0)}, LOW={sev.get('LOW',0)}. "
                f"Top issues: {', '.join(top_titles)}. "
                f"Risk score: {report['risk_score']}/10. "
                "Provide a 2-sentence security assessment for the engineering team."
            )
            result = await rtp(generate_gemini_response, prompt)
            if "text" in result:
                report["gemini_insight"] = result["text"]
    except Exception as exc:
        logger.debug("Gemini insight for vulnscan skipped: %s", exc)

    return report


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

@router.get("/analytics")
async def get_analytics() -> dict:
    """Aggregate VulnScan statistics across all scans."""
    try:
        conn = vulnscan_db._get_conn()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(DISTINCT s.id)                                        AS total_scans,
                    COUNT(DISTINCT s.id) FILTER (WHERE s.status='completed')    AS completed_scans,
                    COUNT(f.id)                                                 AS total_findings,
                    COUNT(f.id) FILTER (WHERE f.severity='CRITICAL')            AS critical,
                    COUNT(f.id) FILTER (WHERE f.severity='HIGH')                AS high,
                    COUNT(f.id) FILTER (WHERE f.severity='MEDIUM')              AS medium,
                    COUNT(f.id) FILTER (WHERE f.severity='LOW')                 AS low,
                    COUNT(DISTINCT s.organization)                              AS orgs_scanned
                FROM vulnscan_scans s
                LEFT JOIN vulnscan_findings f ON f.scan_id = s.id
                """
            )
            row = cur.fetchone()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={"error": str(exc)}) from exc

    return {
        "total_scans":     row[0] or 0,
        "completed_scans": row[1] or 0,
        "total_findings":  row[2] or 0,
        "severity_breakdown": {
            "critical": row[3] or 0,
            "high":     row[4] or 0,
            "medium":   row[5] or 0,
            "low":      row[6] or 0,
        },
        "orgs_scanned": row[7] or 0,
    }