"""
VulnScan — XSS (Cross-Site Scripting) module.
Detects reflected XSS via URL params and DOM-sink patterns in HTML.
Passive detection only — uses non-executing canary strings.
"""

from __future__ import annotations

import re
from typing import List, Set
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from bs4 import BeautifulSoup

from backend.app.services.vulnscan.modules.base import BaseScanner
from backend.app.services.vulnscan.models import VulnFinding

# Canary string that is safe yet uniquely identifiable in the reflection
_XSS_CANARY = "VulnScanXSSProbe<script>alert(1)</script>"
_XSS_CANARY_ENCODED = "VulnScanXSSProbe%3Cscript%3Ealert%281%29%3C%2Fscript%3E"

# Patterns indicating the canary was reflected without encoding
_REFLECTED_PATTERNS = [
    re.compile(r"VulnScanXSSProbe<script>", re.IGNORECASE),
    re.compile(r"VulnScanXSSProbe%3Cscript%3E", re.IGNORECASE),
]

# DOM-based XSS sink signatures
_DOM_SINK_PATTERNS = [
    (re.compile(r"document\.write\s*\(", re.IGNORECASE), "document.write()"),
    (re.compile(r"\.innerHTML\s*=", re.IGNORECASE), ".innerHTML assignment"),
    (re.compile(r"\.outerHTML\s*=", re.IGNORECASE), ".outerHTML assignment"),
    (re.compile(r"eval\s*\(", re.IGNORECASE), "eval()"),
    (re.compile(r"setTimeout\s*\(\s*['\"]", re.IGNORECASE), "setTimeout with string"),
    (re.compile(r"setInterval\s*\(\s*['\"]", re.IGNORECASE), "setInterval with string"),
    (re.compile(r"location\.href\s*=", re.IGNORECASE), "location.href assignment"),
    (re.compile(r"location\.replace\s*\(", re.IGNORECASE), "location.replace()"),
    (re.compile(r"dangerouslySetInnerHTML", re.IGNORECASE), "React dangerouslySetInnerHTML"),
    (re.compile(r"\$\s*\(\s*location", re.IGNORECASE), "jQuery with location object"),
]


class XSSScanner(BaseScanner):
    MODULE_NAME = "xss"

    async def scan(self) -> List[VulnFinding]:
        findings: List[VulnFinding] = []
        tested_params: Set[str] = set()

        # 1. Reflected XSS — URL query parameters
        parsed = urlparse(self.target_url)
        qs = parse_qs(parsed.query, keep_blank_values=True)

        for param in qs:
            if param in tested_params:
                continue
            tested_params.add(param)

            injected_qs = dict(qs)
            injected_qs[param] = _XSS_CANARY
            injected_url = urlunparse(
                parsed._replace(query=urlencode(injected_qs, doseq=True))
            )

            try:
                resp = await self.client.get(injected_url)
                if self._is_reflected(resp.text):
                    findings.append(
                        self._finding(
                            title=f"Reflected XSS — URL Parameter '{param}'",
                            severity="HIGH",
                            description=(
                                f"The URL parameter '{param}' reflects user input without HTML-encoding. "
                                "An attacker can craft a malicious link that executes JavaScript in the victim's browser."
                            ),
                            remediation=(
                                "HTML-encode all output. Use a templating engine with auto-escaping (Jinja2, Handlebars). "
                                "Implement a strict Content-Security-Policy. "
                                "Validate/sanitise input on the server side."
                            ),
                            cwe_id="CWE-79",
                            cvss_score=7.4,
                            evidence=self._extract_reflection(resp.text),
                            affected_url=injected_url,
                            parameter=param,
                            references=[
                                "https://owasp.org/www-community/attacks/xss/",
                                "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html",
                            ],
                        )
                    )
            except Exception as exc:
                self._log.debug("XSS probe error for param '%s': %s", param, exc)

        # 2. Reflected XSS — Form inputs
        try:
            page_resp = await self.client.get(self.target_url)
            html = page_resp.text
        except Exception as exc:
            self._log.debug("Could not fetch page for XSS form scan: %s", exc)
            html = ""

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for form in soup.find_all("form"):
                action = form.get("action") or self.target_url
                method = (form.get("method") or "get").upper()
                form_data = {}
                inputs = form.find_all(["input", "textarea"])
                for inp in inputs:
                    name = inp.get("name")
                    if not name:
                        continue
                    form_data[name] = inp.get("value", "test")

                for inp in inputs:
                    name = inp.get("name")
                    input_type = (inp.get("type") or "text").lower()
                    if not name or input_type in {"hidden", "submit", "button", "file"}:
                        continue
                    if name in tested_params:
                        continue
                    tested_params.add(name)

                    test_data = dict(form_data)
                    test_data[name] = _XSS_CANARY

                    try:
                        if method == "POST":
                            resp = await self.client.post(action, data=test_data)
                        else:
                            resp = await self.client.get(action, params=test_data)

                        if self._is_reflected(resp.text):
                            findings.append(
                                self._finding(
                                    title=f"Reflected XSS — Form Input '{name}'",
                                    severity="HIGH",
                                    description=(
                                        f"The form field '{name}' (method={method}) reflects input unencoded. "
                                        "An attacker could submit a crafted form or trick a victim into submitting it, executing JavaScript."
                                    ),
                                    remediation=(
                                        "HTML-encode all output. Use CSRF protection on forms. "
                                        "Deploy a Content-Security-Policy to mitigate impact."
                                    ),
                                    cwe_id="CWE-79",
                                    cvss_score=7.4,
                                    evidence=self._extract_reflection(resp.text),
                                    affected_url=str(action),
                                    parameter=name,
                                    references=[
                                        "https://owasp.org/www-community/attacks/xss/",
                                    ],
                                )
                            )
                    except Exception as exc:
                        self._log.debug("XSS form probe error for '%s': %s", name, exc)

            # 3. DOM-based XSS sinks (static pattern analysis in page source)
            script_blocks = soup.find_all("script")
            dom_sinks_found: Set[str] = set()
            for script in script_blocks:
                src = script.string or ""
                for pattern, sink_name in _DOM_SINK_PATTERNS:
                    if pattern.search(src) and sink_name not in dom_sinks_found:
                        dom_sinks_found.add(sink_name)
                        findings.append(
                            self._finding(
                                title=f"Potential DOM-Based XSS Sink: {sink_name}",
                                severity="MEDIUM",
                                description=(
                                    f"The page source contains a dangerous JavaScript sink '{sink_name}'. "
                                    "If user-controlled input reaches this sink, DOM-based XSS is possible."
                                ),
                                remediation=(
                                    f"Audit all data flows reaching '{sink_name}'. "
                                    "Use safe DOM APIs (textContent, setAttribute). "
                                    "Avoid passing user input to dangerous functions."
                                ),
                                cwe_id="CWE-79",
                                cvss_score=6.1,
                                references=[
                                    "https://owasp.org/www-community/attacks/DOM_Based_XSS",
                                ],
                            )
                        )

        return findings

    # ------------------------------------------------------------------

    def _is_reflected(self, body: str) -> bool:
        return any(p.search(body) for p in _REFLECTED_PATTERNS)

    def _extract_reflection(self, body: str, max_len: int = 300) -> str:
        for pattern in _REFLECTED_PATTERNS:
            m = pattern.search(body)
            if m:
                start = max(0, m.start() - 30)
                end = min(len(body), m.end() + 100)
                return body[start:end].replace("\n", " ").strip()[:max_len]
        return "(canary reflected)"