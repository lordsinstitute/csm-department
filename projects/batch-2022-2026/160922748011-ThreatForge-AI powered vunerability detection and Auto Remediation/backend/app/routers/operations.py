"""API routers exposing core CognitoForge Labs functionality.

Payload cheat sheet for frontend devs:
- POST /upload_repo -> {"repo_id": str, "repo_url"?: str, "zip_file_base64"?: str}
- POST /simulate_attack -> {"repo_id": str}
- GET  /reports/{repo_id}/latest -> summary JSON with run_id + severity tallies
"""

from __future__ import annotations

import json
import logging
import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel

from backend.app.integrations import supabase_service as snowflake_integration

from backend.app.core.settings import get_settings
from backend.app.models.schemas import (
    AttackPlan,
    AttackStep,
    RepoUpload,
    SimulationRun,
    SimulationReport,
    SimulationSummary,
    VulnerabilityReport,
)
from backend.app.services import repo_fetcher
from backend.app.services.gemini_service import (
    generate_attack_plan,
    generate_ai_insight,
    generate_gemini_attack_plan,
    generate_gemini_response,
)
from backend.app.services.gradient_service import run_gradient_task
from backend.app.services.sandbox_service import run_sandbox_simulation
from backend.app.services.snowflake_service import find_vulnerabilities_for_repo, list_all_vulnerabilities
from backend.app.utils.storage import (
    SimulationDataError,
    SimulationNotFoundError,
    ensure_simulation_dir,
    list_simulations,
    load_simulation,
)


class SimulateAttackRequest(BaseModel):
    """Request payload for generating an attack simulation."""

    repo_id: str
    force: bool = False  # Force new generation, bypass cache


# Cache for recent attack plan generations (repo_id -> {timestamp, plan_data})
# Plans cached for < 10 minutes to avoid excessive Gemini API calls
_attack_plan_cache: dict[str, dict] = {}


class SimulationRunResponse(SimulationRun):
    gradient: dict[str, object]


def _to_dict(model: BaseModel) -> dict[str, object]:
    """Return a plain dict regardless of Pydantic major version."""

    if hasattr(model, "model_dump"):
        return model.model_dump()  # Pydantic v2

    return model.dict()  # Pydantic v1 fallback


logger = logging.getLogger(__name__)

REPO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
SEVERITY_BUCKETS = ("critical", "high", "medium", "low")


def _persist_simulation(run: SimulationRun) -> None:
    """Persist the simulation payload as JSON so future requests can fetch it."""

    directory = ensure_simulation_dir()
    file_path = directory / f"{run.run_id}.json"
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(jsonable_encoder(run), handle, indent=2)


def _build_report(run: SimulationRun) -> SimulationReport:
    """Construct a report summary from a stored simulation run."""

    severity_counts = Counter(step.severity.lower() for step in run.plan.steps)
    summary = {
        "overall_severity": run.plan.overall_severity,
    }
    for severity, count in severity_counts.items():
        summary[f"{severity}_steps"] = count

    affected_files = sorted({file for step in run.plan.steps for file in step.affected_files})
    summary["affected_files"] = affected_files

    return SimulationReport(repo_id=run.repo_id, run_id=run.run_id, summary=summary)


async def _attach_ai_insight(run: SimulationRun, report: SimulationReport) -> Optional[str]:
    """Populate the report with an AI insight when Gemini is enabled."""

    settings = get_settings()
    if not settings.use_gemini:
        return None

    insight = await run_in_threadpool(generate_ai_insight, run, report)
    if insight:
        report.ai_insight = insight
        await run_in_threadpool(
            snowflake_integration.store_ai_insight,
            run.repo_id,
            run.run_id,
            insight,
        )
    return insight


async def _fetch_report_from_snowflake(repo_id: str, run_id: Optional[str] = None) -> Optional[SimulationReport]:
    """Attempt to build a report using Snowflake-sourced data."""

    fetcher = snowflake_integration.fetch_latest_simulation_report
    args: tuple[object, ...] = (repo_id,)
    if run_id is not None:
        fetcher = snowflake_integration.fetch_simulation_report
        args = (repo_id, run_id)

    payload = await run_in_threadpool(fetcher, *args)
    if not payload:
        return None

    summary = payload.get("summary") or {}
    resolved_run_id = str(payload.get("run_id") or run_id or "")
    if not resolved_run_id:
        return None

    report = SimulationReport(repo_id=repo_id, run_id=resolved_run_id, summary=summary)
    insight = payload.get("ai_insight")
    if insight:
        report.ai_insight = insight

    return report


def _blank_severity_counts() -> Dict[str, int]:
    return {severity: 0 for severity in SEVERITY_BUCKETS}


def _compute_local_severity_counts() -> Dict[str, int]:
    """Aggregate severity counts from locally persisted simulations."""

    counts = _blank_severity_counts()
    directory = ensure_simulation_dir()
    for file_path in directory.glob("*.json"):
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            logger.debug("Skipping unreadable simulation file", extra={"file": str(file_path), "error": str(exc)})
            continue

        overall = str(payload.get("plan", {}).get("overall_severity") or "").strip().lower()
        if overall in counts:
            counts[overall] += 1

    return counts


def _validate_repo_id(repo_id: str) -> None:
    """Ensure repository identifiers follow the expected pattern."""

    if not REPO_ID_PATTERN.fullmatch(repo_id):
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid repo_id. Use letters, numbers, underscores, or hyphens."},
        )


router = APIRouter(tags=["operations"])


@router.post("/upload_repo")
async def upload_repo(payload: RepoUpload) -> dict[str, object]:
    """Accept a repository upload request and return an acknowledgement."""

    logger.info("/upload_repo request received", extra={"repo_id": payload.repo_id})
    try:
        if not payload.repo_url and not payload.zip_file_base64:
            detail = {"error": "Either repo_url or zip_file_base64 must be provided"}
            logger.warning(
                "/upload_repo missing repo source",
                extra={"repo_id": payload.repo_id},
            )
            raise HTTPException(status_code=400, detail=detail)

        manifest_summary: Optional[dict[str, object]] = None
        if payload.repo_url:
            try:
                manifest_summary = repo_fetcher.fetch_and_store_repo(payload.repo_id, str(payload.repo_url))
            except repo_fetcher.RepoFetchError as exc:
                logger.exception(
                    "/upload_repo repository fetch failed",
                    extra={"repo_id": payload.repo_id, "repo_url": str(payload.repo_url)},
                )
                raise HTTPException(status_code=502, detail={"error": str(exc)}) from exc

        response = {
            "repo_id": payload.repo_id,
            "status": "ingested",
            "source": "url" if payload.repo_url else "upload",
        }
        if manifest_summary:
            response["files_indexed"] = manifest_summary.get("file_count")
            response["high_risk_files"] = manifest_summary.get("high_risk_file_count")
        logger.info("/upload_repo success", extra={"repo_id": payload.repo_id})
        return response
    except HTTPException:
        logger.exception("/upload_repo failed", extra={"repo_id": payload.repo_id})
        raise
    except Exception as exc:
        logger.exception("Unexpected error during /upload_repo", extra={"repo_id": payload.repo_id})
        raise HTTPException(status_code=500, detail={"error": "Unexpected server error"}) from exc


@router.post("/simulate_attack", response_model=SimulationRunResponse)
async def simulate_attack(request: SimulateAttackRequest) -> dict[str, object]:
    """Generate AI-powered attack plan and sandbox simulation for the requested repository.
    
    Uses Gemini AI (when enabled) to analyze repository structure and generate
    contextual attack scenarios. Falls back to deterministic plan if AI unavailable.
    
    Features:
    - Caching: Returns cached results if generated < 10 minutes ago (unless force=true)
    - AI Insights: Includes Gemini-generated security analysis
    - Metadata: Persists prompts and raw responses for audit trails
    """

    logger.info("/simulate_attack request received", extra={
        "repo_id": request.repo_id,
        "force": request.force
    })
    _validate_repo_id(request.repo_id)

    # Testing instructions:
    # - After change, run uvicorn and hit:
    #   `curl -s -X POST http://127.0.0.1:8000/simulate_attack -H "Content-Type: application/json" -d '{"repo_id":"aptos-meme-nft-minter"}' | jq`
    # - Expected JSON includes top-level "gradient" with "metadata": {"runtime_env": "DigitalOcean Gradient (Simulated)", "instance_type": "g1-small (mock)", "execution_time": <float>}

    try:
        # Check cache for recent simulation (< 10 minutes old)
        cache_key = request.repo_id
        cached_entry = _attack_plan_cache.get(cache_key)
        if not request.force and cached_entry:
            cache_age = (datetime.utcnow() - cached_entry["timestamp"]).total_seconds()
            if cache_age < 600:  # 10 minutes = 600 seconds
                logger.info(
                    "Returning cached attack plan",
                    extra={"repo_id": request.repo_id, "cache_age_seconds": cache_age},
                )
                return cached_entry["simulation_data"]

        plan_dict: Optional[dict] = None
        try:
            manifest = repo_fetcher.load_repo_manifest(request.repo_id)
            high_risk_files = repo_fetcher.select_high_risk_files(manifest, limit=15)

            repo_profile = {
                "repo_id": request.repo_id,
                "manifest": manifest,
                "high_risk_files": high_risk_files,
                "languages": manifest.get("top_extensions", []),
                "dependencies": manifest.get("dependencies", []),
            }

            logger.info(
                "Generating AI attack plan",
                extra={"repo_id": request.repo_id, "high_risk_files": len(high_risk_files)},
            )

            plan_dict = await run_in_threadpool(generate_gemini_attack_plan, repo_profile, 3)
            steps = [
                AttackStep(
                    step_number=step.get("step_number", index + 1),
                    description=step.get("description", ""),
                    technique_id=step.get("technique_id", ""),
                    severity=step.get("severity", "medium"),
                    affected_files=step.get("affected_files", []),
                )
                for index, step in enumerate(plan_dict.get("steps", []))
            ]

            plan = AttackPlan(
                repo_id=request.repo_id,
                overall_severity=plan_dict.get("overall_severity", "high"),
                steps=steps,
            )
        except repo_fetcher.ManifestNotFoundError:
            logger.warning(
                "Repository manifest not found, using legacy attack plan",
                extra={"repo_id": request.repo_id},
            )
            plan = generate_attack_plan(request.repo_id)
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "Gemini attack plan generation failed, using legacy fallback",
                extra={"repo_id": request.repo_id, "error": str(exc)},
            )
            plan = generate_attack_plan(request.repo_id)

        sandbox_result = run_sandbox_simulation(plan)

        timestamp = datetime.utcnow()
        run_id = f"{request.repo_id}_{timestamp.strftime('%Y%m%dT%H%M%S%f')}"
        run_record = SimulationRun(
            repo_id=request.repo_id,
            run_id=run_id,
            timestamp=timestamp,
            plan=plan,
            sandbox=sandbox_result,
        )

        _persist_simulation(run_record)  # Persistence hook sits here so future endpoints can read it back.

        await run_in_threadpool(
            snowflake_integration.store_simulation_run,
            request.repo_id,
            run_id,
            {
                "overall_severity": plan.overall_severity,
                "timestamp": timestamp.isoformat(),
            },
        )

        affected_file_rows = [
            {"file_path": file_path, "severity": step.severity}
            for step in plan.steps
            for file_path in step.affected_files
        ]
        if affected_file_rows:
            await run_in_threadpool(
                snowflake_integration.store_affected_files,
                request.repo_id,
                run_id,
                affected_file_rows,
            )

        plan_summary = (
            plan.model_dump().get("overall_severity")
            if hasattr(plan, "model_dump")
            else plan.dict().get("overall_severity")
        )
        gradient_payload = {
            "repo_id": request.repo_id,
            "run_id": run_id,
            "summary": plan_summary,
        }
        try:
            gradient_result = await run_in_threadpool(
                run_gradient_task,
                "ai_insight",
                gradient_payload,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "Gradient integration failed",
                extra={"repo_id": request.repo_id, "run_id": run_id, "error": str(exc)},
            )
            gradient_result = {"status": "error", "mock": True, "error": str(exc)}

        if gradient_result is None:
            gradient_result = {"status": "unavailable", "mock": True}

        logger.info("Gradient mock result: %s", gradient_result)

        response_payload = _to_dict(run_record)
        response_payload["gradient"] = gradient_result

        _attack_plan_cache[cache_key] = {
            "timestamp": timestamp,
            "simulation_data": response_payload,
        }

        logger.info(
            "/simulate_attack success",
            extra={"repo_id": request.repo_id, "run_id": run_id, "cached": False},
        )
        return response_payload
    except HTTPException:
        logger.exception("/simulate_attack failed", extra={"repo_id": request.repo_id})
        raise
    except Exception as exc:
        logger.exception("Unexpected error during /simulate_attack", extra={"repo_id": request.repo_id})
        raise HTTPException(status_code=500, detail={"error": "Unexpected server error"}) from exc


@router.get("/fetch_report")
async def fetch_report(repo_id: str) -> dict[str, object]:
    """Produce a vulnerability report for the supplied repository."""

    logger.info("/fetch_report request received", extra={"repo_id": repo_id})
    try:
        findings = find_vulnerabilities_for_repo(repo_id)
        if not findings:
            findings = list_all_vulnerabilities()

        report = VulnerabilityReport(repo_id=repo_id, findings=findings)
        logger.info("/fetch_report success", extra={"repo_id": repo_id, "finding_count": len(findings)})
        return _to_dict(report)
    except HTTPException:
        logger.exception("/fetch_report failed", extra={"repo_id": repo_id})
        raise
    except Exception as exc:
        logger.exception("Unexpected error during /fetch_report", extra={"repo_id": repo_id})
        raise HTTPException(status_code=500, detail={"error": "Unexpected server error"}) from exc


@router.get("/simulations/{repo_id}", response_model=List[SimulationSummary])
async def list_simulations_endpoint(repo_id: str) -> List[dict[str, object]]:
    """Return summaries of every stored simulation for the repository."""

    logger.info("/simulations list request received", extra={"repo_id": repo_id})
    _validate_repo_id(repo_id)
    try:
        summaries = list_simulations(repo_id)
        logger.info(
            "/simulations list success",
            extra={"repo_id": repo_id, "count": len(summaries)},
        )
        return [_to_dict(summary) for summary in summaries]
    except SimulationDataError as exc:
        logger.exception("/simulations list data error", extra={"repo_id": repo_id})
        return JSONResponse(status_code=500, content={"error": str(exc)})
    except HTTPException:
        logger.exception("/simulations list failed", extra={"repo_id": repo_id})
        raise
    except Exception as exc:
        logger.exception("Unexpected error listing simulations", extra={"repo_id": repo_id})
        raise HTTPException(status_code=500, detail={"error": "Unexpected server error"}) from exc


@router.get("/reports/{repo_id}/latest", response_model=SimulationReport)
async def get_latest_simulation_report(repo_id: str) -> dict[str, object]:
    """Fetch the most recent simulation run and return its summary report."""

    logger.info("/reports latest request received", extra={"repo_id": repo_id})
    _validate_repo_id(repo_id)
    try:
        snowflake_report = await _fetch_report_from_snowflake(repo_id)
        if snowflake_report:
            if snowflake_report.ai_insight is None:
                try:
                    run = load_simulation(repo_id, snowflake_report.run_id)
                except (SimulationNotFoundError, SimulationDataError) as exc:
                    logger.warning(
                        "/reports latest missing local artefact",
                        extra={"repo_id": repo_id, "run_id": snowflake_report.run_id, "error": str(exc)},
                    )
                else:
                    await _attach_ai_insight(run, snowflake_report)
            logger.info(
                "/reports latest served via Snowflake",
                extra={"repo_id": repo_id, "run_id": snowflake_report.run_id},
            )
            return _to_dict(snowflake_report)

        summaries = list_simulations(repo_id)
        if not summaries:
            logger.warning("/reports latest not found", extra={"repo_id": repo_id})
            raise HTTPException(status_code=404, detail={"error": f"No simulations found for {repo_id}"})

        summaries.sort(key=lambda item: item.timestamp, reverse=True)
        latest_summary = summaries[0]
        logger.info(
            "/reports latest selecting run",
            extra={"repo_id": repo_id, "run_id": latest_summary.run_id},
        )

        run = load_simulation(repo_id, latest_summary.run_id)
        report = _build_report(run)
        insight = await _attach_ai_insight(run, report)
        logger.info(
            "/reports latest success",
            extra={
                "repo_id": repo_id,
                "run_id": latest_summary.run_id,
                "ai_insight_present": bool(insight),
            },
        )
        return _to_dict(report)
    except SimulationNotFoundError as exc:
        logger.warning("/reports latest run missing", extra={"repo_id": repo_id})
        raise HTTPException(status_code=404, detail={"error": str(exc)}) from exc
    except SimulationDataError as exc:
        logger.exception("/reports latest data error", extra={"repo_id": repo_id})
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    except HTTPException:
        logger.exception("/reports latest failed", extra={"repo_id": repo_id})
        raise
    except Exception as exc:
        logger.exception("Unexpected error retrieving latest simulation report", extra={"repo_id": repo_id})
        raise HTTPException(status_code=500, detail={"error": "Unexpected server error"}) from exc


@router.get("/simulations/{repo_id}/{run_id}", response_model=SimulationRun)
async def get_simulation(repo_id: str, run_id: str) -> dict[str, object]:
    """Return the persisted simulation payload for the requested run identifier."""

    logger.info("/simulations detail request received", extra={"repo_id": repo_id, "run_id": run_id})
    _validate_repo_id(repo_id)
    try:
        run = load_simulation(repo_id, run_id)
        logger.info("/simulations detail success", extra={"repo_id": repo_id, "run_id": run_id})
        return _to_dict(run)
    except SimulationNotFoundError as exc:
        logger.warning(
            "/simulations detail not found",
            extra={"repo_id": repo_id, "run_id": run_id},
        )
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except SimulationDataError as exc:
        logger.exception(
            "/simulations detail data error",
            extra={"repo_id": repo_id, "run_id": run_id},
        )
        return JSONResponse(status_code=500, content={"error": str(exc)})
    except HTTPException:
        logger.exception(
            "/simulations detail failed",
            extra={"repo_id": repo_id, "run_id": run_id},
        )
        raise
    except Exception as exc:
        logger.exception(
            "Unexpected error retrieving simulation detail",
            extra={"repo_id": repo_id, "run_id": run_id},
        )
        raise HTTPException(status_code=500, detail={"error": "Unexpected server error"}) from exc


@router.get("/reports/{repo_id}/{run_id}", response_model=SimulationReport)
async def get_simulation_report(repo_id: str, run_id: str) -> dict[str, object]:
    """Produce a structured summary of a persisted simulation run."""

    logger.info("/reports detail request received", extra={"repo_id": repo_id, "run_id": run_id})
    _validate_repo_id(repo_id)
    try:
        snowflake_report = await _fetch_report_from_snowflake(repo_id, run_id)
        if snowflake_report:
            if snowflake_report.ai_insight is None:
                try:
                    run = load_simulation(repo_id, run_id)
                except (SimulationNotFoundError, SimulationDataError) as exc:
                    logger.warning(
                        "/reports detail missing local artefact",
                        extra={"repo_id": repo_id, "run_id": run_id, "error": str(exc)},
                    )
                else:
                    await _attach_ai_insight(run, snowflake_report)
            logger.info(
                "/reports detail served via Snowflake",
                extra={"repo_id": repo_id, "run_id": run_id},
            )
            return _to_dict(snowflake_report)

        run = load_simulation(repo_id, run_id)
        report = _build_report(run)
        insight = await _attach_ai_insight(run, report)
        logger.info(
            "/reports detail success",
            extra={
                "repo_id": repo_id,
                "run_id": run_id,
                "ai_insight_present": bool(insight),
            },
        )
        return _to_dict(report)
    except SimulationNotFoundError as exc:
        logger.warning(
            "/reports detail not found",
            extra={"repo_id": repo_id, "run_id": run_id},
        )
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except SimulationDataError as exc:
        logger.exception(
            "/reports detail data error",
            extra={"repo_id": repo_id, "run_id": run_id},
        )
        return JSONResponse(status_code=500, content={"error": str(exc)})
    except HTTPException:
        logger.exception(
            "/reports detail failed",
            extra={"repo_id": repo_id, "run_id": run_id},
        )
        raise
    except Exception as exc:
        logger.exception(
            "Unexpected error retrieving simulation report",
            extra={"repo_id": repo_id, "run_id": run_id},
        )
        raise HTTPException(status_code=500, detail={"error": "Unexpected server error"}) from exc


@router.get("/analytics/summary")
async def get_analytics_summary() -> Dict[str, int]:
    """Return distribution of simulations by overall severity."""

    logger.info("/analytics summary request received")

    counts = await run_in_threadpool(snowflake_integration.fetch_severity_summary)
    if counts:
        logger.info("/analytics summary served via Snowflake", extra={"counts": counts})
        return counts

    counts = await run_in_threadpool(_compute_local_severity_counts)
    logger.info("/analytics summary served via local fallback", extra={"counts": counts})
    return counts


# ==============================================================================
# Gemini REST API Test Endpoint
# ==============================================================================


class GeminiQueryRequest(BaseModel):
    """Request payload for Gemini REST API query."""
    prompt: str


@router.post("/gemini/query", tags=["gemini"])
async def query_gemini_rest_api(request: GeminiQueryRequest):
    """
    Test endpoint for the new Gemini REST API function.
    
    This endpoint demonstrates usage of the generate_gemini_response() function
    that calls Gemini's REST API directly (not the SDK).
    
    Example request:
        POST /gemini/query
        {
            "prompt": "Explain what a SQL injection attack is"
        }
    
    Example response:
        {
            "text": "SQL injection is a code injection...",
            "model": "gemini-pro",
            "prompt_length": 40,
            "response_length": 150
        }
    """
    logger.info(
        "Gemini REST API query requested",
        extra={"prompt_length": len(request.prompt)}
    )
    
    try:
        # Call the new REST API function
        result = await run_in_threadpool(generate_gemini_response, request.prompt)
        
        if "error" in result:
            logger.error(
                "Gemini REST API returned error",
                extra={"error": result["error"]}
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": result["error"],
                    "details": result.get("details", "No additional details")
                }
            )
        
        # Success response
        return {
            "text": result["text"],
            "model": result.get("model", "unknown"),
            "prompt_length": len(request.prompt),
            "response_length": len(result["text"])
        }
        
    except HTTPException:
        raise
    except ValueError as exc:
        # Configuration error (missing API key)
        logger.error("Gemini configuration error", extra={"error": str(exc)})
        raise HTTPException(
            status_code=500,
            detail={"error": str(exc)}
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error in Gemini query endpoint")
        raise HTTPException(
            status_code=500,
            detail={"error": "Unexpected server error"}
        ) from exc


@router.get("/api/simulations/list")
async def list_all_simulations() -> dict[str, object]:
    """List all simulation files for dashboard analytics."""
    
    try:
        directory = ensure_simulation_dir()
        simulations = []
        
        # Read all JSON files in simulations directory
        for file_path in directory.glob("*.json"):
            try:
                with file_path.open("r", encoding="utf-8") as handle:
                    simulation_data = json.load(handle)
                    simulations.append(simulation_data)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to read simulation file {file_path}: {e}")
                continue
        
        # Sort by timestamp (newest first)
        simulations.sort(
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )
        
        logger.info(f"Listed {len(simulations)} simulations for dashboard")
        
        return {
            "success": True,
            "total": len(simulations),
            "simulations": simulations
        }
    
    except Exception as exc:
        logger.exception("Failed to list simulations")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to list simulations"}
        ) from exc


@router.get("/api/gradient/status")
async def get_gradient_status() -> dict[str, object]:
    """Get DigitalOcean Gradient cluster status."""
    
    try:
        from backend.app.services.gradient_service import get_gradient_status
        
        status = await run_in_threadpool(get_gradient_status)
        logger.info("Gradient status fetched successfully")
        
        return {
            "success": True,
            "status": status
        }
    
    except Exception as exc:
        logger.exception("Failed to fetch Gradient status")
        return {
            "success": False,
            "error": str(exc),
            "status": {
                "connected": False,
                "mock_mode": True,
                "message": "Gradient service unavailable"
            }
        }


# ==============================================================================
# Dashboard endpoints — all metrics sourced from the database
# ==============================================================================


@router.get("/api/dashboard/metrics")
async def get_dashboard_metrics() -> dict[str, object]:
    """
    Return aggregated Security Dashboard KPIs pulled directly from the database.

    Response shape:
    {
        "success": true,
        "data": {
            "repos_analyzed":          int,
            "total_scans":             int,
            "total_vulnerabilities":   int,
            "vulnerability_distribution": {"critical": int, "high": int, "medium": int, "low": int},
            "avg_risk_score":          float,
            "gemini_scans":            int,
            "fallback_scans":          int,
            "last_scan":               str | null
        }
    }
    """
    logger.info("/api/dashboard/metrics request received")
    try:
        metrics = await run_in_threadpool(snowflake_integration.fetch_dashboard_metrics)
        logger.info("/api/dashboard/metrics success", extra={"metrics": metrics})
        return {"success": True, "data": metrics}
    except Exception as exc:
        logger.exception("Unexpected error fetching dashboard metrics")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to fetch dashboard metrics"},
        ) from exc


@router.get("/api/dashboard/recent-simulations")
async def get_recent_simulations(limit: int = 5) -> dict[str, object]:
    """
    Return the most recent simulation runs for the dashboard's Recent Simulations panel.

    Query param:
        limit (int, default 5) — how many rows to return

    Response shape:
    {
        "success": true,
        "data": [
            {
                "run_id":           str,
                "repo_id":          str,
                "overall_severity": str,
                "timestamp":        str | null,
                "total_steps":      int,
                "plan_source":      "gemini" | "fallback",
                "ai_insight":       str | null
            },
            ...
        ]
    }
    """
    logger.info("/api/dashboard/recent-simulations request received", extra={"limit": limit})
    try:
        simulations = await run_in_threadpool(
            snowflake_integration.fetch_recent_simulations, limit
        )
        logger.info(
            "/api/dashboard/recent-simulations success",
            extra={"count": len(simulations)},
        )
        return {"success": True, "data": simulations}
    except Exception as exc:
        logger.exception("Unexpected error fetching recent simulations")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to fetch recent simulations"},
        ) from exc