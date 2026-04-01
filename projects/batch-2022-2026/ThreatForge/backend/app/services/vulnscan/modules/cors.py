"""
VulnScan — CORS Misconfiguration module.
Checks for wildcard and reflected-origin Access-Control-Allow-Origin policies.
"""

from __future__ import annotations

from typing import List

from backend.app.services.vulnscan.modules.base import BaseScanner
from backend.app.services.vulnscan.models import VulnFinding

_EVIL_ORIGIN = "https://evil-vulnscan-probe.com"


class CORSScanner(BaseScanner):
    MODULE_NAME = "cors"

    async def scan(self) -> List[VulnFinding]:
        findings: List[VulnFinding] = []

        try:
            # 1. Probe with an attacker-controlled origin
            headers = {"Origin": _EVIL_ORIGIN}
            resp = await self.client.get(self.target_url, headers=headers)
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
        except Exception as exc:
            self._log.debug("CORS probe failed: %s", exc)
            return findings

        acao = resp_headers.get("access-control-allow-origin", "")
        acac = resp_headers.get("access-control-allow-credentials", "").lower()

        # Wildcard — all origins allowed
        if acao == "*":
            findings.append(
                self._finding(
                    title="CORS Wildcard Origin Allowed (Access-Control-Allow-Origin: *)",
                    severity="MEDIUM",
                    description=(
                        "The server responds with `Access-Control-Allow-Origin: *`, allowing any origin to "
                        "read the response. This is acceptable for fully public APIs but is a vulnerability "
                        "for endpoints that return user-specific data."
                    ),
                    remediation=(
                        "Restrict `Access-Control-Allow-Origin` to known, trusted origins. "
                        "Use an allowlist and reflect only validated origins."
                    ),
                    cwe_id="CWE-942",
                    cvss_score=5.3,
                    evidence=f"Access-Control-Allow-Origin: {acao}",
                    references=[
                        "https://owasp.org/www-community/attacks/CORS_OriginHeaderScrutiny",
                        "https://portswigger.net/web-security/cors",
                    ],
                )
            )

        # Reflected origin — server echoes back whatever origin is sent
        elif acao == _EVIL_ORIGIN:
            severity = "CRITICAL" if acac == "true" else "HIGH"
            cvss = 9.1 if acac == "true" else 7.5
            extra = (
                " The server also sends `Access-Control-Allow-Credentials: true`, enabling cross-origin "
                "requests that carry cookies and authentication headers. This is a critical misconfiguration."
                if acac == "true"
                else ""
            )
            findings.append(
                self._finding(
                    title="CORS — Arbitrary Origin Reflected (Access-Control-Allow-Origin: <attacker>)",
                    severity=severity,
                    description=(
                        "The server reflects the attacker-supplied `Origin` header back in "
                        "`Access-Control-Allow-Origin`. Any origin can read responses from this server." + extra
                    ),
                    remediation=(
                        "Maintain an explicit allowlist of trusted origins. "
                        "Never reflect the `Origin` header without validation. "
                        "Only send `Access-Control-Allow-Credentials: true` for explicitly trusted origins."
                    ),
                    cwe_id="CWE-942",
                    cvss_score=cvss,
                    evidence=(
                        f"Request Origin: {_EVIL_ORIGIN}\n"
                        f"Response Access-Control-Allow-Origin: {acao}\n"
                        f"Response Access-Control-Allow-Credentials: {acac}"
                    ),
                    references=[
                        "https://portswigger.net/web-security/cors",
                        "https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html#cross-origin-resource-sharing",
                    ],
                )
            )

        # `null` origin allowed (sandbox iframe trick)
        elif acao.strip().lower() == "null":
            findings.append(
                self._finding(
                    title="CORS Allows 'null' Origin",
                    severity="HIGH",
                    description=(
                        "The server responds with `Access-Control-Allow-Origin: null`. "
                        "An attacker can trigger a `null` origin from a sandboxed iframe and read the response."
                    ),
                    remediation=(
                        "Do not allowlist the `null` origin. Use an explicit origin allowlist."
                    ),
                    cwe_id="CWE-942",
                    cvss_score=7.5,
                    evidence=f"Access-Control-Allow-Origin: {acao}",
                    references=["https://portswigger.net/web-security/cors"],
                )
            )

        return findings