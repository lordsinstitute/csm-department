"""
VulnScan — Additional scanner modules.
Covers: CSRF, Open Redirect, Clickjacking, Broken Auth, SSRF, XXE.
Each class is self-contained and follows the BaseScanner interface.
"""

from __future__ import annotations

import re
from typing import List
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from bs4 import BeautifulSoup

from backend.app.services.vulnscan.models import VulnFinding
from backend.app.services.vulnscan.modules.base import BaseScanner


# ==============================================================================
# CSRF Scanner
# ==============================================================================

class CSRFScanner(BaseScanner):
    """
    Detects POST forms that lack CSRF token fields.
    Passive detection only — does not submit forms.
    """

    MODULE_NAME = "csrf"

    # Names commonly used for CSRF tokens
    _TOKEN_NAMES = {
        "csrf", "csrftoken", "csrf_token", "_token", "authenticity_token",
        "xsrf-token", "_csrf", "csrfmiddlewaretoken", "requestverificationtoken",
        "__requestverificationtoken", "nonce",
    }

    # Header-based CSRF protection
    _CSRF_HEADERS = {"x-csrf-token", "x-xsrf-token", "x-requested-with"}

    async def scan(self) -> List[VulnFinding]:
        findings: List[VulnFinding] = []

        try:
            resp = await self.client.get(self.target_url)
            soup = BeautifulSoup(resp.text, "html.parser")
        except Exception as exc:
            self._log.debug("CSRF scan fetch error: %s", exc)
            return findings

        for form in soup.find_all("form"):
            method = (form.get("method") or "get").upper()
            if method != "POST":
                continue

            # Collect all input names (lower-cased)
            input_names = {
                (inp.get("name") or "").lower()
                for inp in form.find_all("input")
            }

            # Check for CSRF token field
            has_token = any(name in self._TOKEN_NAMES for name in input_names)

            if not has_token:
                action = form.get("action") or self.target_url
                findings.append(
                    self._finding(
                        title="CSRF Token Missing in POST Form",
                        severity="HIGH",
                        description=(
                            f"A POST form with action `{action}` does not contain a CSRF token field. "
                            "An attacker can trick an authenticated user into submitting this form from a third-party site."
                        ),
                        remediation=(
                            "Add a unique, unpredictable CSRF token to every state-changing form. "
                            "Validate the token server-side on every POST/PUT/DELETE request. "
                            "Use a framework-level CSRF middleware (Django CsrfViewMiddleware, Laravel CSRF, Spring Security)."
                        ),
                        cwe_id="CWE-352",
                        cvss_score=8.8,
                        affected_url=str(action),
                        references=[
                            "https://owasp.org/www-community/attacks/csrf",
                            "https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html",
                        ],
                    )
                )

        return findings


# ==============================================================================
# Open Redirect Scanner
# ==============================================================================

_REDIRECT_PARAMS = [
    "next", "redirect", "redirect_url", "redirect_uri", "return",
    "returnurl", "return_url", "goto", "destination", "dest", "url",
    "link", "callback", "forward", "location", "to",
]

_REDIRECT_PROBE = "https://evil-vulnscan-probe.com"


class OpenRedirectScanner(BaseScanner):
    """Detects open redirect vulnerabilities in URL parameters."""

    MODULE_NAME = "open_redirect"

    async def scan(self) -> List[VulnFinding]:
        findings: List[VulnFinding] = []
        parsed = urlparse(self.target_url)
        qs = parse_qs(parsed.query, keep_blank_values=True)

        # Try known redirect params not already in the query string
        params_to_test = set(_REDIRECT_PARAMS) | set(qs.keys())

        for param in params_to_test:
            injected_qs = dict(qs)
            injected_qs[param] = _REDIRECT_PROBE
            test_url = urlunparse(
                parsed._replace(query=urlencode(injected_qs, doseq=True))
            )

            try:
                resp = await self.client.get(test_url)
                final_url = str(resp.url)

                if _REDIRECT_PROBE in final_url:
                    findings.append(
                        self._finding(
                            title=f"Open Redirect — Parameter '{param}'",
                            severity="MEDIUM",
                            description=(
                                f"The parameter '{param}' can redirect users to an arbitrary URL. "
                                "Attackers use open redirects in phishing campaigns: a legitimate-looking link "
                                "on your domain silently forwards users to a malicious site."
                            ),
                            remediation=(
                                "Validate redirect URLs against an allowlist of trusted domains. "
                                "Use relative paths instead of full URLs for redirects. "
                                "Never redirect to a URL provided directly by user input."
                            ),
                            cwe_id="CWE-601",
                            cvss_score=6.1,
                            evidence=f"Redirected to: {final_url}",
                            affected_url=test_url,
                            parameter=param,
                            references=[
                                "https://owasp.org/www-community/attacks/Unvalidated_Redirects_and_Forwards_Cheat_Sheet",
                            ],
                        )
                    )
                    break  # One finding per scan is enough
            except Exception as exc:
                self._log.debug("Open redirect probe error for '%s': %s", param, exc)

        return findings


# ==============================================================================
# Clickjacking Scanner
# ==============================================================================

class ClickjackingScanner(BaseScanner):
    """
    Checks whether the page can be framed (clickjacking risk).
    Examines X-Frame-Options and CSP frame-ancestors.
    """

    MODULE_NAME = "clickjacking"

    async def scan(self) -> List[VulnFinding]:
        findings: List[VulnFinding] = []

        try:
            resp = await self.client.get(self.target_url)
            headers = {k.lower(): v.lower() for k, v in resp.headers.items()}
        except Exception as exc:
            self._log.debug("Clickjacking scan fetch error: %s", exc)
            return findings

        xfo = headers.get("x-frame-options", "")
        csp = headers.get("content-security-policy", "")
        has_frame_ancestors = "frame-ancestors" in csp

        if not xfo and not has_frame_ancestors:
            findings.append(
                self._finding(
                    title="Clickjacking Protection Missing (No X-Frame-Options or CSP frame-ancestors)",
                    severity="MEDIUM",
                    description=(
                        "Neither the `X-Frame-Options` header nor a `Content-Security-Policy: frame-ancestors` "
                        "directive was detected. The page can be embedded in an invisible iframe by an attacker "
                        "and used to trick authenticated users into clicking interface elements."
                    ),
                    remediation=(
                        "Add `X-Frame-Options: DENY` (or `SAMEORIGIN`) to all responses. "
                        "Alternatively, use `Content-Security-Policy: frame-ancestors 'none'` which is more flexible. "
                        "Prefer the CSP approach for modern browsers."
                    ),
                    cwe_id="CWE-1021",
                    cvss_score=6.1,
                    references=[
                        "https://owasp.org/www-community/attacks/Clickjacking",
                        "https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html",
                    ],
                )
            )
        elif xfo and xfo not in {"deny", "sameorigin"}:
            findings.append(
                self._finding(
                    title=f"Weak X-Frame-Options Value: '{xfo}'",
                    severity="LOW",
                    description=(
                        f"The X-Frame-Options header has an unusual value: `{xfo}`. "
                        "Only `DENY` and `SAMEORIGIN` are universally supported."
                    ),
                    remediation="Use `X-Frame-Options: DENY` or `X-Frame-Options: SAMEORIGIN`.",
                    cwe_id="CWE-1021",
                    cvss_score=3.7,
                )
            )

        return findings


# ==============================================================================
# Broken Auth / Session Cookie Scanner
# ==============================================================================

class BrokenAuthScanner(BaseScanner):
    """
    Checks session cookies for missing security flags: Secure, HttpOnly, SameSite.
    """

    MODULE_NAME = "broken_auth"

    async def scan(self) -> List[VulnFinding]:
        findings: List[VulnFinding] = []

        try:
            resp = await self.client.get(self.target_url)
        except Exception as exc:
            self._log.debug("Broken auth scan fetch error: %s", exc)
            return findings

        cookies = resp.cookies
        set_cookie_headers = resp.headers.get_list("set-cookie") if hasattr(resp.headers, "get_list") else []

        # httpx stores cookies in the jar; also parse raw Set-Cookie for flag analysis
        raw_cookies = [v for k, v in resp.headers.items() if k.lower() == "set-cookie"]

        for raw in raw_cookies:
            cookie_name = raw.split("=")[0].strip()
            raw_lower = raw.lower()

            if "secure" not in raw_lower:
                findings.append(
                    self._finding(
                        title=f"Session Cookie Missing 'Secure' Flag: {cookie_name}",
                        severity="HIGH",
                        description=(
                            f"The cookie '{cookie_name}' is set without the `Secure` flag. "
                            "It can be transmitted over plain HTTP, exposing session tokens to network eavesdropping."
                        ),
                        remediation=(
                            "Set the `Secure` flag on all sensitive cookies. "
                            "Ensure HTTPS is enforced site-wide."
                        ),
                        cwe_id="CWE-614",
                        cvss_score=7.5,
                        evidence=f"Set-Cookie: {raw[:200]}",
                        references=[
                            "https://owasp.org/www-community/controls/SecureCookieAttribute",
                        ],
                    )
                )

            if "httponly" not in raw_lower:
                findings.append(
                    self._finding(
                        title=f"Session Cookie Missing 'HttpOnly' Flag: {cookie_name}",
                        severity="HIGH",
                        description=(
                            f"The cookie '{cookie_name}' is set without the `HttpOnly` flag. "
                            "JavaScript can read this cookie, enabling theft via XSS."
                        ),
                        remediation=(
                            "Set `HttpOnly` on all session cookies to prevent JavaScript access."
                        ),
                        cwe_id="CWE-1004",
                        cvss_score=6.5,
                        evidence=f"Set-Cookie: {raw[:200]}",
                    )
                )

            if "samesite" not in raw_lower:
                findings.append(
                    self._finding(
                        title=f"Session Cookie Missing 'SameSite' Attribute: {cookie_name}",
                        severity="MEDIUM",
                        description=(
                            f"The cookie '{cookie_name}' has no `SameSite` attribute. "
                            "Without SameSite, the cookie is sent with cross-origin requests, "
                            "making CSRF attacks easier."
                        ),
                        remediation=(
                            "Set `SameSite=Strict` or `SameSite=Lax` on session cookies."
                        ),
                        cwe_id="CWE-352",
                        cvss_score=5.4,
                        evidence=f"Set-Cookie: {raw[:200]}",
                    )
                )

        return findings


# ==============================================================================
# SSRF Scanner
# ==============================================================================

_SSRF_PARAMS = [
    "url", "uri", "src", "source", "href", "dest", "destination",
    "redirect", "redirect_url", "return", "next", "link", "host",
    "proxy", "fetch", "load", "get", "request", "callback", "image",
    "img", "file", "path", "endpoint", "api", "service", "webhook",
]


class SSRFScanner(BaseScanner):
    """
    Heuristically detects SSRF-prone URL parameters.
    Note: Full SSRF confirmation requires an out-of-band callback server
    which is outside the scope of passive scanning.
    """

    MODULE_NAME = "ssrf"

    async def scan(self) -> List[VulnFinding]:
        findings: List[VulnFinding] = []
        parsed = urlparse(self.target_url)
        qs = parse_qs(parsed.query, keep_blank_values=True)

        ssrf_params = [p for p in qs if p.lower() in _SSRF_PARAMS]

        if ssrf_params:
            findings.append(
                self._finding(
                    title=f"Potential SSRF-Prone URL Parameters Detected: {', '.join(ssrf_params)}",
                    severity="MEDIUM",
                    description=(
                        f"The URL contains parameter(s) ({', '.join(ssrf_params)}) that accept URL or path values. "
                        "If the server fetches the provided URL without validation, an attacker can access "
                        "internal services, cloud metadata endpoints (169.254.169.254), and private network resources."
                    ),
                    remediation=(
                        "Validate and allowlist URLs that the server is permitted to fetch. "
                        "Block requests to private IP ranges (127.0.0.0/8, 10.0.0.0/8, 169.254.0.0/16). "
                        "Use an egress proxy with URL filtering. "
                        "Disable unnecessary URL-fetching functionality."
                    ),
                    cwe_id="CWE-918",
                    cvss_score=8.6,
                    parameter=", ".join(ssrf_params),
                    references=[
                        "https://owasp.org/www-community/attacks/Server_Side_Request_Forgery",
                        "https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html",
                    ],
                )
            )

        return findings


# ==============================================================================
# XXE Scanner
# ==============================================================================

_XML_CONTENT_TYPES = {"text/xml", "application/xml", "application/xhtml+xml"}


class XXEScanner(BaseScanner):
    """
    Detects endpoints that may accept XML input (potential XXE).
    Uses OPTIONS request and content-type detection.
    Passive only — does not submit an XXE payload.
    """

    MODULE_NAME = "xxe"

    async def scan(self) -> List[VulnFinding]:
        findings: List[VulnFinding] = []

        # 1. OPTIONS probe — does the server accept XML?
        try:
            resp = await self.client.options(self.target_url)
            allow = resp.headers.get("allow", "").upper()
            accepts = resp.headers.get("accept", "")
            content_type = resp.headers.get("content-type", "")

            is_xml_possible = (
                any(ct in content_type for ct in _XML_CONTENT_TYPES)
                or any(ct in accepts for ct in _XML_CONTENT_TYPES)
                or "POST" in allow
            )

            if is_xml_possible:
                findings.append(
                    self._finding(
                        title="Potential XML Endpoint Detected — XXE Risk Requires Manual Verification",
                        severity="MEDIUM",
                        description=(
                            "The endpoint appears to accept or return XML content. "
                            "If the server parses XML without disabling external entity processing, "
                            "it is vulnerable to XXE (XML External Entity) injection. "
                            "XXE can lead to file disclosure, SSRF, and denial of service."
                        ),
                        remediation=(
                            "Disable external entity processing in your XML parser: "
                            "set `feature_external_ges` and `feature_external_pes` to False. "
                            "Use a safe alternative like JSON where possible. "
                            "Validate and sanitise all XML input."
                        ),
                        cwe_id="CWE-611",
                        cvss_score=7.5,
                        evidence=(
                            f"OPTIONS Allow: {allow}\n"
                            f"Content-Type: {content_type}\n"
                            f"Accept: {accepts}"
                        ),
                        references=[
                            "https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing",
                            "https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html",
                        ],
                    )
                )
        except Exception as exc:
            self._log.debug("XXE OPTIONS probe failed: %s", exc)

        return findings