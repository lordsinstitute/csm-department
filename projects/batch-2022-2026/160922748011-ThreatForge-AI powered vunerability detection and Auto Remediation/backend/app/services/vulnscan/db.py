"""
VulnScan database persistence layer.
Uses the same Supabase/PostgreSQL connection as supabase_service.py.
All tables are prefixed vulnscan_ and owned by this service.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import execute_values

from backend.app.core.settings import get_settings
from backend.app.services.vulnscan.schemas import (
    FindingOut,
    ScanOut,
    ScanSummary,
    VulnScanReport,
)

# ---------------------------------------------------------------------------
# Connection (shared with supabase_service pattern)
# ---------------------------------------------------------------------------

_conn = None
_lock = Lock()


def _get_conn():
    global _conn
    if _conn is not None:
        try:
            _conn.cursor().execute("SELECT 1")
            return _conn
        except Exception:
            _conn = None

    with _lock:
        if _conn is not None:
            return _conn

        settings = get_settings()
        if not all([
            settings.supabase_db_host,
            settings.supabase_db_name,
            settings.supabase_db_user,
            settings.supabase_db_password,
        ]):
            raise RuntimeError(
                "VulnScan: Supabase DB_* env vars are not fully configured. "
                "Set DB_HOST, DB_NAME, DB_USER, DB_PASSWORD."
            )

        _conn = psycopg2.connect(
            host=settings.supabase_db_host,
            dbname=settings.supabase_db_name,
            user=settings.supabase_db_user,
            password=settings.supabase_db_password,
            port=settings.supabase_db_port or 5432,
        )
        _conn.autocommit = True
        return _conn


# ---------------------------------------------------------------------------
# Scan CRUD
# ---------------------------------------------------------------------------

def create_scan(
    target_url: str,
    scan_type: str,
    modules_requested: List[str],
    requester_name: str,
    organization: str,
    notes: Optional[str] = None,
) -> str:
    """Insert a new scan record and return its UUID."""
    scan_id = str(uuid.uuid4())
    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO vulnscan_scans
                (id, target_url, scan_type, status, consent_confirmed,
                 requester_name, organization, notes, modules_requested, modules_completed)
            VALUES (%s, %s, %s, 'queued', TRUE, %s, %s, %s, %s::jsonb, '[]'::jsonb)
            """,
            (
                scan_id,
                target_url,
                scan_type,
                requester_name,
                organization,
                notes,
                json.dumps(modules_requested),
            ),
        )
    return scan_id


def update_scan_status(
    scan_id: str,
    status: str,
    modules_completed: Optional[List[str]] = None,
    error_message: Optional[str] = None,
) -> None:
    conn = _get_conn()
    now = datetime.utcnow()
    with conn.cursor() as cur:
        if status == "running":
            cur.execute(
                "UPDATE vulnscan_scans SET status=%s, started_at=%s WHERE id=%s",
                (status, now, scan_id),
            )
        elif status in ("completed", "failed"):
            cur.execute(
                """
                UPDATE vulnscan_scans
                SET status=%s, completed_at=%s,
                    modules_completed=%s::jsonb,
                    error_message=%s
                WHERE id=%s
                """,
                (
                    status,
                    now,
                    json.dumps(modules_completed or []),
                    error_message,
                    scan_id,
                ),
            )
        else:
            cur.execute(
                "UPDATE vulnscan_scans SET status=%s WHERE id=%s",
                (status, scan_id),
            )


def store_findings(scan_id: str, findings: List[Dict[str, Any]]) -> None:
    """Bulk-insert findings for a completed scan."""
    if not findings:
        return

    rows = [
        (
            str(uuid.uuid4()),
            scan_id,
            f["module"],
            f["title"],
            f["severity"],
            f.get("cvss_score"),
            f.get("cve_id"),
            f.get("cwe_id"),
            f["description"],
            f.get("evidence"),
            f.get("affected_url"),
            f.get("parameter"),
            f["remediation"],
            json.dumps(f.get("references", [])),
        )
        for f in findings
    ]

    conn = _get_conn()
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO vulnscan_findings
                (id, scan_id, module, title, severity, cvss_score, cve_id, cwe_id,
                 description, evidence, affected_url, parameter, remediation, reference_links)
            VALUES %s
            """,
            rows,
        )


# ---------------------------------------------------------------------------
# Read helpers
# ---------------------------------------------------------------------------

def _row_to_scan_summary(row: tuple) -> Dict[str, Any]:
    (
        id_, target_url, scan_type, status, requester_name,
        organization, created_at, completed_at,
        total, critical, high, medium, low, info,
    ) = row
    return {
        "id": id_,
        "target_url": target_url,
        "scan_type": scan_type,
        "status": status,
        "requester_name": requester_name,
        "organization": organization,
        "created_at": created_at,
        "completed_at": completed_at,
        "total_findings": total or 0,
        "critical": critical or 0,
        "high": high or 0,
        "medium": medium or 0,
        "low": low or 0,
        "info": info or 0,
    }


def list_scans(limit: int = 50, status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = _get_conn()
    where = "WHERE s.status = %s" if status else ""
    params = (status, limit) if status else (limit,)
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT
                s.id, s.target_url, s.scan_type, s.status,
                s.requester_name, s.organization,
                s.created_at, s.completed_at,
                COUNT(f.id) AS total,
                COUNT(f.id) FILTER (WHERE f.severity='CRITICAL') AS critical,
                COUNT(f.id) FILTER (WHERE f.severity='HIGH')     AS high,
                COUNT(f.id) FILTER (WHERE f.severity='MEDIUM')   AS medium,
                COUNT(f.id) FILTER (WHERE f.severity='LOW')      AS low,
                COUNT(f.id) FILTER (WHERE f.severity='INFO')     AS info
            FROM vulnscan_scans s
            LEFT JOIN vulnscan_findings f ON f.scan_id = s.id
            {where}
            GROUP BY s.id
            ORDER BY s.created_at DESC
            LIMIT %s
            """,
            params,
        )
        return [_row_to_scan_summary(r) for r in cur.fetchall()]


def get_scan(scan_id: str) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                id, target_url, scan_type, status,
                requester_name, organization, notes,
                modules_requested, modules_completed,
                created_at, started_at, completed_at, error_message
            FROM vulnscan_scans WHERE id = %s
            """,
            (scan_id,),
        )
        row = cur.fetchone()
    if not row:
        return None
    (
        id_, target_url, scan_type, status,
        requester_name, organization, notes,
        modules_requested, modules_completed,
        created_at, started_at, completed_at, error_message,
    ) = row
    return {
        "id": id_,
        "target_url": target_url,
        "scan_type": scan_type,
        "status": status,
        "requester_name": requester_name,
        "organization": organization,
        "notes": notes,
        "modules_requested": modules_requested or [],
        "modules_completed": modules_completed or [],
        "created_at": created_at,
        "started_at": started_at,
        "completed_at": completed_at,
        "error_message": error_message,
    }


def get_findings(
    scan_id: str,
    severity: Optional[str] = None,
    module: Optional[str] = None,
) -> List[Dict[str, Any]]:
    conn = _get_conn()
    conditions = ["scan_id = %s"]
    params: List[Any] = [scan_id]
    if severity:
        conditions.append("severity = %s")
        params.append(severity.upper())
    if module:
        conditions.append("module = %s")
        params.append(module)

    where = " AND ".join(conditions)
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT id, scan_id, module, title, severity,
                   cvss_score, cve_id, cwe_id, description,
                   evidence, affected_url, parameter, remediation,
                   reference_links, discovered_at
            FROM vulnscan_findings
            WHERE {where}
            ORDER BY
                CASE severity
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH'     THEN 2
                    WHEN 'MEDIUM'   THEN 3
                    WHEN 'LOW'      THEN 4
                    ELSE 5
                END,
                discovered_at DESC
            """,
            params,
        )
        rows = cur.fetchall()

    return [
        {
            "id": r[0], "scan_id": r[1], "module": r[2], "title": r[3],
            "severity": r[4], "cvss_score": r[5], "cve_id": r[6], "cwe_id": r[7],
            "description": r[8], "evidence": r[9], "affected_url": r[10],
            "parameter": r[11], "remediation": r[12],
            "reference_links": r[13] or [], "discovered_at": r[14],
        }
        for r in rows
    ]


def build_report(scan_id: str, gemini_insight: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Assemble a full VulnScanReport dict for the given scan."""
    scan = get_scan(scan_id)
    if not scan:
        return None

    findings = get_findings(scan_id)

    severity_weights = {"CRITICAL": 10, "HIGH": 7, "MEDIUM": 4, "LOW": 1, "INFO": 0}
    total_weight = sum(severity_weights.get(f["severity"], 0) for f in findings)
    risk_score = min(10.0, round(total_weight / max(len(findings), 1) * 0.7, 1)) if findings else 0.0

    sev_summary = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for f in findings:
        sev_summary[f["severity"]] = sev_summary.get(f["severity"], 0) + 1

    priority = [f for f in findings if f["severity"] in ("CRITICAL", "HIGH")][:5]

    return {
        "scan_id": scan_id,
        "target_url": scan["target_url"],
        "organization": scan["organization"],
        "requester_name": scan["requester_name"],
        "scan_type": scan["scan_type"],
        "started_at": scan["started_at"],
        "completed_at": scan["completed_at"],
        "risk_score": risk_score,
        "severity_summary": sev_summary,
        "priority_findings": priority,
        "all_findings": findings,
        "modules_run": scan["modules_completed"] or [],
        "gemini_insight": gemini_insight,
    }