"""
VulnScan base scanner module.
All scanner modules must subclass BaseScanner and implement `scan()`.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, List

from backend.app.services.vulnscan.models import VulnFinding

logger = logging.getLogger(__name__)


class BaseScanner(ABC):
    """
    Abstract base class for all VulnScan modules.

    Subclasses implement ``scan()`` which returns a list of ``VulnFinding`` objects.
    The public ``run()`` method wraps ``scan()`` with error handling and logging so
    individual modules never need to worry about crashing the orchestrator.
    """

    #: Must be overridden in each subclass — used in log messages
    MODULE_NAME: str = "base"

    def __init__(self, target_url: str, client: Any) -> None:
        self.target_url = target_url.rstrip("/")
        self.client = client
        self._log = logging.getLogger(f"vulnscan.{self.MODULE_NAME}")

    @abstractmethod
    async def scan(self) -> List[VulnFinding]:
        """Perform the actual vulnerability scan. Must be implemented by subclasses."""

    async def run(self) -> List[VulnFinding]:
        """
        Execute the scan with unified error handling.
        Returns an empty list on failure so the orchestrator keeps running.
        """
        try:
            findings = await self.scan()
            self._log.debug(
                "Module finished",
                extra={"scanner_module": self.MODULE_NAME, "findings": len(findings)},
            )
            return findings
        except Exception as exc:  # noqa: BLE001
            self._log.exception(
                "Module raised an unhandled exception",
                extra={"scanner_module": self.MODULE_NAME},
                exc_info=exc,
            )
            return []

    # ------------------------------------------------------------------
    # Helpers available to all subclasses
    # ------------------------------------------------------------------

    def _finding(
        self,
        title: str,
        severity: str,
        description: str,
        remediation: str,
        *,
        cvss_score: float | None = None,
        cve_id: str | None = None,
        cwe_id: str | None = None,
        evidence: str | None = None,
        affected_url: str | None = None,
        parameter: str | None = None,
        references: list[str] | None = None,
    ) -> VulnFinding:
        """Convenience factory so subclasses don't repeat boilerplate."""
        return VulnFinding(
            module=self.MODULE_NAME,
            title=title,
            severity=severity,
            description=description,
            remediation=remediation,
            cvss_score=cvss_score,
            cve_id=cve_id,
            cwe_id=cwe_id,
            evidence=evidence,
            affected_url=affected_url or self.target_url,
            parameter=parameter,
            reference_links=references or [],
        )