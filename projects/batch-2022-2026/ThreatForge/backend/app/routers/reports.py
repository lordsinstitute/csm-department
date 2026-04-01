

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


# ─────────────────────────────────────────────────────────────────────────────
# Vulnerability Scan  (affected_files + ai_insights)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/vulnerability")
async def list_vulnerability_reports(limit: int = 50):
    from backend.app.integrations.supabase_service import list_vulnerability_scans
    try:
        scans = await run_in_threadpool(list_vulnerability_scans, limit)
        return {"total": len(scans), "scans": scans}
    except Exception as exc:
        logger.exception("Error listing vulnerability scans")
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc


@router.get("/vulnerability/{run_id}")
async def get_vulnerability_report(run_id: str):
    from backend.app.integrations.supabase_service import fetch_vulnerability_report
    try:
        report = await run_in_threadpool(fetch_vulnerability_report, run_id)
    except Exception as exc:
        logger.exception("Error fetching vulnerability report %s", run_id)
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    if not report:
        raise HTTPException(status_code=404, detail={"error": f"Run '{run_id}' not found"})
    return report


# ─────────────────────────────────────────────────────────────────────────────
# Performance Test  (performance_runs)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/performance")
async def list_performance_reports(limit: int = 50):
    from backend.app.integrations.supabase_service import list_performance_scans
    try:
        runs = await run_in_threadpool(list_performance_scans, limit)
        return {"total": len(runs), "runs": runs}
    except Exception as exc:
        logger.exception("Error listing performance scans")
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc


@router.get("/performance/{run_id}")
async def get_performance_report(run_id: str):
    from backend.app.integrations.supabase_service import fetch_performance_report_full
    try:
        report = await run_in_threadpool(fetch_performance_report_full, run_id)
    except Exception as exc:
        logger.exception("Error fetching performance report %s", run_id)
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    if not report:
        raise HTTPException(status_code=404, detail={"error": f"Run '{run_id}' not found"})
    return report


# ─────────────────────────────────────────────────────────────────────────────
# Intrusion Test  (vulnscan_scans + vulnscan_findings)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/intrusion")
async def list_intrusion_reports(limit: int = 50):
    from backend.app.integrations.supabase_service import list_intrusion_scans
    try:
        scans = await run_in_threadpool(list_intrusion_scans, limit)
        return {"total": len(scans), "scans": scans}
    except Exception as exc:
        logger.exception("Error listing intrusion scans")
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc


@router.get("/intrusion/{scan_id}")
async def get_intrusion_report(scan_id: str):
    from backend.app.integrations.supabase_service import fetch_intrusion_report
    try:
        report = await run_in_threadpool(fetch_intrusion_report, scan_id)
    except Exception as exc:
        logger.exception("Error fetching intrusion report %s", scan_id)
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    if not report:
        raise HTTPException(status_code=404, detail={"error": f"Scan '{scan_id}' not found"})
    return report