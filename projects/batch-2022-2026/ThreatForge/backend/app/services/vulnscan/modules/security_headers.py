"""
VulnScan — Security Headers module.
Checks for the presence and correct configuration of HTTP security headers.
Passive detection only — no modification of requests beyond a simple GET.
"""

from __future__ import annotations

from typing import List

from backend.app.services.vulnscan.modules.base import BaseScanner
from backend.app.services.vulnscan.models import VulnFinding

# ---------------------------------------------------------------------------
# Header definitions
# ---------------------------------------------------------------------------

# (header_name, required_present, title, severity, cwe, cvss, description, remediation, refs)
_REQUIRED_HEADERS = [
    (
        "strict-transport-security",
        "Strict-Transport-Security (HSTS) Missing",
        "HIGH",
        "CWE-319",
        7.5,
        "The Strict-Transport-Security header is absent. Without HSTS, browsers may connect over plain HTTP, exposing users to protocol downgrade and man-in-the-middle attacks.",
        "Add `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` to all HTTPS responses.",
        ["https://owasp.org/www-project-secure-headers/", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security"],
    ),
    (
        "x-content-type-options",
        "X-Content-Type-Options Missing",
        "MEDIUM",
        "CWE-693",
        5.3,
        "The X-Content-Type-Options header is not set. This allows browsers to MIME-sniff responses away from the declared content type, enabling certain XSS vectors.",
        "Set `X-Content-Type-Options: nosniff` on all responses.",
        ["https://owasp.org/www-project-secure-headers/"],
    ),
    (
        "x-frame-options",
        "X-Frame-Options Missing",
        "MEDIUM",
        "CWE-1021",
        6.1,
        "X-Frame-Options is absent. The page may be embedded in an iframe by an attacker and used for clickjacking.",
        "Add `X-Frame-Options: DENY` or `SAMEORIGIN`, or use `Content-Security-Policy: frame-ancestors 'none'`.",
        ["https://owasp.org/www-community/attacks/Clickjacking"],
    ),
    (
        "content-security-policy",
        "Content-Security-Policy (CSP) Missing",
        "HIGH",
        "CWE-693",
        7.2,
        "No Content-Security-Policy header was found. Without CSP, the application is more susceptible to cross-site scripting (XSS) and data injection attacks.",
        "Define a strict CSP policy. Start with `default-src 'self'` and add only required sources.",
        ["https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP", "https://csp-evaluator.withgoogle.com/"],
    ),
    (
        "referrer-policy",
        "Referrer-Policy Missing",
        "LOW",
        "CWE-200",
        3.7,
        "The Referrer-Policy header is absent. This may cause sensitive URL fragments to be leaked in Referer headers sent to third parties.",
        "Set `Referrer-Policy: strict-origin-when-cross-origin` or `no-referrer`.",
        ["https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy"],
    ),
    (
        "permissions-policy",
        "Permissions-Policy Missing",
        "LOW",
        "CWE-693",
        3.1,
        "Permissions-Policy (formerly Feature-Policy) is absent. Browser features such as camera, geolocation, and microphone are not explicitly restricted.",
        "Add `Permissions-Policy: geolocation=(), microphone=(), camera=()` (adjust per application needs).",
        ["https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy"],
    ),
    (
        "cross-origin-opener-policy",
        "Cross-Origin-Opener-Policy (COOP) Missing",
        "LOW",
        "CWE-693",
        3.1,
        "COOP is absent, leaving the browsing context group open to cross-origin information leaks (e.g. Spectre-style attacks).",
        "Add `Cross-Origin-Opener-Policy: same-origin` to isolate the page's browsing context.",
        ["https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cross-Origin-Opener-Policy"],
    ),
    (
        "cross-origin-resource-policy",
        "Cross-Origin-Resource-Policy (CORP) Missing",
        "LOW",
        "CWE-693",
        3.1,
        "CORP is absent. Resources served by this origin may be loaded cross-origin, enabling side-channel read attacks.",
        "Add `Cross-Origin-Resource-Policy: same-origin` or `same-site` to restrict resource loading.",
        ["https://developer.mozilla.org/en-US/docs/Web/HTTP/Cross-Origin_Resource_Policy"],
    ),
    (
        "cache-control",
        "Cache-Control Not Set for Sensitive Content",
        "LOW",
        "CWE-524",
        3.7,
        "No Cache-Control directive was detected. Sensitive pages may be cached by proxies or shared browsers.",
        "For authenticated/sensitive pages use `Cache-Control: no-store, no-cache, must-revalidate`.",
        ["https://owasp.org/www-project-web-security-testing-guide/"],
    ),
]

# Headers that should NOT be present (information disclosure)
_DANGEROUS_HEADERS = [
    (
        "x-powered-by",
        "X-Powered-By Header Exposes Technology Stack",
        "LOW",
        "CWE-200",
        3.7,
        "The X-Powered-By header is present and discloses the server-side technology (e.g. PHP, ASP.NET). Attackers can use this to target known vulnerabilities.",
        "Remove the X-Powered-By header in server/framework configuration.",
        ["https://owasp.org/www-project-web-security-testing-guide/"],
    ),
    (
        "server",
        "Server Header Reveals Version Information",
        "LOW",
        "CWE-200",
        3.7,
        "The Server header discloses web server software and version, giving attackers a head start in targeting known exploits.",
        "Configure the web server to suppress or anonymise the Server header.",
        ["https://owasp.org/www-project-web-security-testing-guide/"],
    ),
    (
        "x-aspnet-version",
        "X-AspNet-Version Header Exposes Framework Version",
        "LOW",
        "CWE-200",
        3.7,
        "The X-AspNet-Version header reveals the exact .NET framework version in use.",
        "Disable this header via `<httpRuntime enableVersionHeader=\"false\" />` in web.config.",
        [],
    ),
    (
        "x-aspnetmvc-version",
        "X-AspNetMvc-Version Header Exposes MVC Version",
        "LOW",
        "CWE-200",
        3.7,
        "The X-AspNetMvc-Version header discloses the ASP.NET MVC version.",
        "Call `MvcHandler.DisableMvcResponseHeader = true;` in Global.asax.",
        [],
    ),
]


class SecurityHeadersScanner(BaseScanner):
    MODULE_NAME = "security_headers"

    async def scan(self) -> List[VulnFinding]:
        findings: List[VulnFinding] = []

        try:
            response = await self.client.get(self.target_url)
        except Exception as exc:
            self._log.warning("Could not fetch %s: %s", self.target_url, exc)
            return findings

        headers_lower = {k.lower(): v for k, v in response.headers.items()}

        # Check for missing required headers
        for (hdr, title, severity, cwe, cvss, description, remediation, refs) in _REQUIRED_HEADERS:
            if hdr not in headers_lower:
                findings.append(
                    self._finding(
                        title=title,
                        severity=severity,
                        description=description,
                        remediation=remediation,
                        cwe_id=cwe,
                        cvss_score=cvss,
                        evidence=f"Header '{hdr}' was absent in the response.",
                        references=refs,
                    )
                )

        # Check for dangerous headers that should be removed
        for (hdr, title, severity, cwe, cvss, description, remediation, refs) in _DANGEROUS_HEADERS:
            if hdr in headers_lower:
                findings.append(
                    self._finding(
                        title=title,
                        severity=severity,
                        description=description,
                        remediation=remediation,
                        cwe_id=cwe,
                        cvss_score=cvss,
                        evidence=f"Header '{hdr}: {headers_lower[hdr]}' was present in the response.",
                        references=refs,
                    )
                )

        # Flag weak CSP if present but with unsafe directives
        csp = headers_lower.get("content-security-policy", "")
        if csp:
            if "unsafe-inline" in csp:
                findings.append(
                    self._finding(
                        title="Content-Security-Policy Uses 'unsafe-inline'",
                        severity="MEDIUM",
                        description="The CSP header contains 'unsafe-inline', which allows inline scripts and styles. This significantly weakens the XSS protection CSP is meant to provide.",
                        remediation="Remove 'unsafe-inline' from the CSP and use nonces or hashes for inline scripts instead.",
                        cwe_id="CWE-693",
                        cvss_score=5.4,
                        evidence=f"CSP: {csp[:300]}",
                        references=["https://csp-evaluator.withgoogle.com/"],
                    )
                )
            if "unsafe-eval" in csp:
                findings.append(
                    self._finding(
                        title="Content-Security-Policy Uses 'unsafe-eval'",
                        severity="MEDIUM",
                        description="The CSP header permits 'unsafe-eval', enabling dynamic code evaluation (eval(), Function(), setTimeout with strings). This creates XSS risk.",
                        remediation="Remove 'unsafe-eval' from CSP. Refactor code that relies on eval().",
                        cwe_id="CWE-693",
                        cvss_score=5.4,
                        evidence=f"CSP: {csp[:300]}",
                        references=["https://csp-evaluator.withgoogle.com/"],
                    )
                )

        return findings