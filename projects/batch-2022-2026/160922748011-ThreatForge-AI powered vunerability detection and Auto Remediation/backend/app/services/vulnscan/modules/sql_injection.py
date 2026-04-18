"""
VulnScan — SQL Injection module.
Error-based detection on URL query parameters and HTML form inputs.
Passive detection only — uses non-destructive payloads that trigger DB errors.
"""

from __future__ import annotations

import re
from typing import List, Set
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from bs4 import BeautifulSoup

from backend.app.services.vulnscan.modules.base import BaseScanner
from backend.app.services.vulnscan.models import VulnFinding

# Error-based SQLi detection payloads (no data destruction, just syntax breaks)
_SQLI_PROBES = [
    "'",
    "''",
    "`",
    '"',
    "1'1",
    "1 OR 1=1--",
    "1; SELECT 1--",
    "' OR '1'='1",
]

# Signatures from common database error messages
_ERROR_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"you have an error in your sql syntax",
        r"warning: mysql",
        r"unclosed quotation mark",
        r"quoted string not properly terminated",
        r"pg_query\(\):",
        r"psycopg2\.errors",
        r"oci_parse\(\) expects",
        r"microsoft ole db provider for sql server",
        r"sqlite3\.operationalerror",
        r"sqliteexception",
        r"odbc sql server driver",
        r"invalid column name",
        r"ora-\d{5}",
        r"db2 sql error",
        r"supplied argument is not a valid mysql",
        r"jdbc\.sqlserverexception",
        r"syntax error.*sql",
        r"unexpected end of sql command",
    ]
]


class SQLInjectionScanner(BaseScanner):
    MODULE_NAME = "sql_injection"

    async def scan(self) -> List[VulnFinding]:
        findings: List[VulnFinding] = []
        tested_params: Set[str] = set()

        # 1. URL query-string parameters
        parsed = urlparse(self.target_url)
        qs = parse_qs(parsed.query, keep_blank_values=True)

        for param, values in qs.items():
            if param in tested_params:
                continue
            tested_params.add(param)
            original_value = values[0] if values else ""

            for probe in _SQLI_PROBES:
                injected_qs = dict(qs)
                injected_qs[param] = probe
                injected_url = urlunparse(
                    parsed._replace(query=urlencode(injected_qs, doseq=True))
                )
                vuln = await self._probe_url(injected_url, param, probe, "GET (query string)")
                if vuln:
                    findings.append(vuln)
                    break  # One finding per param is enough

        # 2. HTML form inputs
        try:
            response = await self.client.get(self.target_url)
            soup = BeautifulSoup(response.text, "html.parser")
        except Exception as exc:
            self._log.debug("Could not parse HTML at %s: %s", self.target_url, exc)
            return findings

        for form in soup.find_all("form"):
            action = form.get("action", self.target_url)
            method = (form.get("method") or "get").upper()

            # Build base form data
            form_data = {}
            inputs = form.find_all(["input", "textarea", "select"])
            for inp in inputs:
                name = inp.get("name")
                if not name:
                    continue
                val = inp.get("value", "test")
                form_data[name] = val

            # Probe each text-type input
            for inp in inputs:
                name = inp.get("name")
                input_type = (inp.get("type") or "text").lower()
                if not name or input_type in {"hidden", "submit", "button", "checkbox", "radio", "file"}:
                    continue
                if name in tested_params:
                    continue
                tested_params.add(name)

                for probe in _SQLI_PROBES:
                    test_data = dict(form_data)
                    test_data[name] = probe

                    try:
                        if method == "POST":
                            resp = await self.client.post(action, data=test_data)
                        else:
                            resp = await self.client.get(action, params=test_data)

                        if self._has_sql_error(resp.text):
                            findings.append(
                                self._finding(
                                    title=f"SQL Injection — Form Input '{name}'",
                                    severity="CRITICAL",
                                    description=(
                                        f"The form field '{name}' (method={method}) is vulnerable to SQL injection. "
                                        "A database error message was triggered by a malformed query fragment."
                                    ),
                                    remediation=(
                                        "Use parameterised queries / prepared statements. "
                                        "Never concatenate user input into SQL strings. "
                                        "Apply an ORM (SQLAlchemy, Hibernate) or stored procedures."
                                    ),
                                    cwe_id="CWE-89",
                                    cve_id=None,
                                    cvss_score=9.8,
                                    evidence=self._extract_error(resp.text),
                                    affected_url=str(action),
                                    parameter=name,
                                    references=[
                                        "https://owasp.org/www-community/attacks/SQL_Injection",
                                        "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
                                    ],
                                )
                            )
                            break
                    except Exception as exc:
                        self._log.debug("Form probe error for param '%s': %s", name, exc)

        return findings

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _probe_url(
        self, url: str, param: str, probe: str, context: str
    ):
        try:
            resp = await self.client.get(url)
            if self._has_sql_error(resp.text):
                return self._finding(
                    title=f"SQL Injection — URL Parameter '{param}'",
                    severity="CRITICAL",
                    description=(
                        f"The URL parameter '{param}' ({context}) is vulnerable to SQL injection. "
                        "Database error output was detected in the server response."
                    ),
                    remediation=(
                        "Use parameterised queries / prepared statements. "
                        "Sanitise and validate all input. "
                        "Do not expose database error messages to users."
                    ),
                    cwe_id="CWE-89",
                    cvss_score=9.8,
                    evidence=self._extract_error(resp.text),
                    affected_url=url,
                    parameter=param,
                    references=[
                        "https://owasp.org/www-community/attacks/SQL_Injection",
                        "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
                    ],
                )
        except Exception as exc:
            self._log.debug("Probe error for url '%s': %s", url, exc)
        return None

    def _has_sql_error(self, body: str) -> bool:
        return any(p.search(body) for p in _ERROR_PATTERNS)

    def _extract_error(self, body: str, max_len: int = 300) -> str:
        for pattern in _ERROR_PATTERNS:
            m = pattern.search(body)
            if m:
                start = max(0, m.start() - 50)
                end = min(len(body), m.end() + 150)
                snippet = body[start:end].replace("\n", " ").strip()
                return snippet[:max_len]
        return "(error detected but could not extract snippet)"