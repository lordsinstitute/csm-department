"""
VulnScan scan orchestrator.
Runs enabled scanner modules against a target URL and persists findings.
All modules are passive detection only — no exploitation.
"""

from __future__ import annotations

import asyncio
import importlib
import logging
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from backend.app.services.vulnscan.modules.base import BaseScanner, VulnFinding
from backend.app.services.vulnscan.schemas import (
    FULL_SCAN_MODULES,
    QUICK_SCAN_MODULES,
    ScanModule,
    ScanType,
)
from backend.app.services.vulnscan.utils.http_client import build_client
from backend.app.services.vulnscan import db as vulnscan_db

logger = logging.getLogger(__name__)

# Map module names to their scanner classes (lazy-imported)
MODULE_CLASS_MAP: Dict[str, str] = {
    ScanModule.SECURITY_HEADERS.value: "backend.app.services.vulnscan.modules.security_headers.SecurityHeadersScanner",
    ScanModule.SSL_TLS.value:          "backend.app.services.vulnscan.modules.ssl_tls.SSLTLSScanner",
    ScanModule.SQL_INJECTION.value:    "backend.app.services.vulnscan.modules.sql_injection.SQLInjectionScanner",
    ScanModule.XSS.value:              "backend.app.services.vulnscan.modules.xss.XSSScanner",
    ScanModule.PAYMENT_GATEWAY.value:  "backend.app.services.vulnscan.modules.payment_gateway.PaymentGatewayScanner",
    ScanModule.CORS.value:             "backend.app.services.vulnscan.modules.cors.CORSScanner",
    ScanModule.SENSITIVE_DATA.value:   "backend.app.services.vulnscan.modules.sensitive_data.SensitiveDataScanner",
    ScanModule.CSRF.value:             "backend.app.services.vulnscan.modules.additional_modules.CSRFScanner",
    ScanModule.OPEN_REDIRECT.value:    "backend.app.services.vulnscan.modules.additional_modules.OpenRedirectScanner",
    ScanModule.CLICKJACKING.value:     "backend.app.services.vulnscan.modules.additional_modules.ClickjackingScanner",
    ScanModule.BROKEN_AUTH.value:      "backend.app.services.vulnscan.modules.additional_modules.BrokenAuthScanner",
    ScanModule.SSRF.value:             "backend.app.services.vulnscan.modules.additional_modules.SSRFScanner",
    ScanModule.XXE.value:              "backend.app.services.vulnscan.modules.additional_modules.XXEScanner",
}

# Concurrency limit — run at most N modules simultaneously
_SEMAPHORE = asyncio.Semaphore(5)


def _load_scanner_class(dotted_path: str) -> type:
    module_path, class_name = dotted_path.rsplit(".", 1)
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


def _resolve_modules(scan_type: str, requested: Optional[List[str]]) -> List[str]:
    if requested:
        return requested
    if scan_type == ScanType.QUICK.value:
        return QUICK_SCAN_MODULES
    return FULL_SCAN_MODULES


async def _run_module(
    module_name: str,
    target_url: str,
    client: Any,
) -> List[VulnFinding]:
    dotted = MODULE_CLASS_MAP.get(module_name)
    if not dotted:
        logger.warning("Unknown VulnScan module: %s — skipping", module_name)
        return []

    try:
        cls = _load_scanner_class(dotted)
        scanner: BaseScanner = cls(target_url, client)
        async with _SEMAPHORE:
            return await scanner.run()
    except Exception as exc:
        logger.exception("VulnScan module %s failed", module_name, exc_info=exc)
        return []


async def run_scan(scan_id: str, target_url: str, scan_type: str, modules: List[str]) -> None:
    """
    Execute all requested modules and persist findings.
    Called as a FastAPI BackgroundTask — must not raise.
    """
    logger.info("VulnScan started", extra={"scan_id": scan_id, "target": target_url})
    vulnscan_db.update_scan_status(scan_id, "running")

    completed_modules: List[str] = []
    all_findings: List[Dict] = []

    try:
        async with build_client() as client:
            tasks = {
                module_name: asyncio.create_task(
                    _run_module(module_name, target_url, client)
                )
                for module_name in modules
            }

            for module_name, task in tasks.items():
                try:
                    findings = await task
                    for f in findings:
                        all_findings.append(
                            {
                                "module":      f.module,
                                "title":       f.title,
                                "severity":    f.severity,
                                "description": f.description,
                                "remediation": f.remediation,
                                "cvss_score":  f.cvss_score,
                                "cve_id":      f.cve_id,
                                "cwe_id":      f.cwe_id,
                                "evidence":    f.evidence,
                                "affected_url":f.affected_url,
                                "parameter":   f.parameter,
                                "references":  f.reference_links,
                            }
                        )
                    completed_modules.append(module_name)
                    logger.debug(
                        "Module complete",
                        extra={"module": module_name, "findings": len(findings)},
                    )
                except Exception as exc:
                    logger.exception("Module task %s raised", module_name, exc_info=exc)

        vulnscan_db.store_findings(scan_id, all_findings)
        vulnscan_db.update_scan_status(scan_id, "completed", completed_modules)
        logger.info(
            "VulnScan completed",
            extra={
                "scan_id": scan_id,
                "modules": len(completed_modules),
                "findings": len(all_findings),
            },
        )

    except Exception as exc:
        logger.exception("VulnScan run failed for %s", scan_id, exc_info=exc)
        vulnscan_db.update_scan_status(
            scan_id, "failed",
            completed_modules,
            error_message=str(exc),
        )