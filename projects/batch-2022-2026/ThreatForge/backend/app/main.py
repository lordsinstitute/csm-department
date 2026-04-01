"""Entry point for the CognitoForge Labs FastAPI application."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.settings import get_settings
from backend.app.integrations.supabase_service import init_snowflake
from backend.app.routers import ai, operations, performance
from backend.app.services.gradient_service import init_gradient, run_gradient_task
import os
from backend.app.routers import code_assist
from backend.app.routers import vulnscan
from backend.app.routers import reports

settings = get_settings()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CognitoForge Labs",
    version="0.1.0",
    description="Hackathon backend for AI-driven DevSecOps red team simulations.",
)

# Basic CORS support so the hackathon frontend can call these endpoints without hassle.
allowed_origins = {
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "https://major-drab.vercel.app",
    "https://major-gi2s8fjth-murtuzamaazs-projects.vercel.app/",
}
if settings.auth0_domain:
    allowed_origins.add(settings.auth0_domain.rstrip("/"))

# Allow extra origins to be provided via environment variable so deploy targets
# (Vercel, Netlify, etc.) can be whitelisted without code changes. Use a
# comma-separated list of origins, e.g.:
#   COGNITOFORGE_ALLOWED_ORIGINS=https://cognitoforge-ai.vercel.app,https://other
extra = os.environ.get("COGNITOFORGE_ALLOWED_ORIGINS")
if extra:
    for origin in (o.strip() for o in extra.split(",")):
        if origin:
            allowed_origins.add(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(operations.router)
app.include_router(ai.router)
app.include_router(performance.router) 
app.include_router(code_assist.router)
app.include_router(vulnscan.router)
app.include_router(reports.router)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialise optional integrations once the application boots."""

    try:
        client = init_snowflake()
        if client is not None:
            logger.info("Supabase integration initialised")
        else:
            logger.debug("Supabase integration skipped (configuration missing or connector absent)")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Supabase integration initialisation failed", extra={"error": str(exc)})

    try:
        init_gradient()
        logger.debug("Gradient task handler ready", extra={"callable": run_gradient_task.__name__})
    except Exception as exc:  # noqa: BLE001
        logger.exception("Gradient integration initialisation failed", extra={"error": str(exc)})
        
    try:
        logger.info("Code Assist service ready")
    except Exception as exc:
        logger.warning(f"Code Assist initialization skipped: {exc}")





@app.get("/health")
async def healthcheck() -> dict[str, bool]:
    """Simple health endpoint for uptime monitoring."""

    return {"ok": True}
