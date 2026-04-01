"""
VulnScan — Payment Gateway / PCI-DSS module.
Checks for card data leakage, insecure payment integration, and common secret key patterns.
Passive detection only — reads responses but does not submit any card data.
"""

from __future__ import annotations

import re
from typing import List

from backend.app.services.vulnscan.models import VulnFinding
from backend.app.services.vulnscan.modules.base import BaseScanner

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# PAN (Primary Account Number) — Luhn-valid card numbers in HTML/JSON
_CARD_PATTERNS = [
    re.compile(r"\b4[0-9]{12}(?:[0-9]{3})?\b"),                  # Visa
    re.compile(r"\b(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}\b"),  # Mastercard
    re.compile(r"\b3[47][0-9]{13}\b"),                            # Amex
    re.compile(r"\b3(?:0[0-5]|[68][0-9])[0-9]{11}\b"),           # Diners
    re.compile(r"\b6(?:011|5[0-9]{2})[0-9]{12}\b"),              # Discover
    re.compile(r"\b(?:2131|1800|35\d{3})\d{11}\b"),              # JCB
]

# Secret / API key patterns for popular payment providers
_SECRET_PATTERNS = [
    (re.compile(r"sk_live_[0-9a-zA-Z]{24,}"),     "Stripe Live Secret Key",         "CRITICAL"),
    (re.compile(r"sk_test_[0-9a-zA-Z]{24,}"),     "Stripe Test Secret Key",         "HIGH"),
    (re.compile(r"rk_live_[0-9a-zA-Z]{24,}"),     "Stripe Restricted Live Key",     "CRITICAL"),
    (re.compile(r"pk_live_[0-9a-zA-Z]{24,}"),     "Stripe Live Publishable Key",    "MEDIUM"),
    (re.compile(r"access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}"),
                                                    "PayPal Production Access Token", "CRITICAL"),
    (re.compile(r"sq0atp-[0-9a-zA-Z\-_]{22}"),    "Square Access Token",            "CRITICAL"),
    (re.compile(r"sq0csp-[0-9a-zA-Z\-_]{43}"),    "Square OAuth Secret",            "CRITICAL"),
    (re.compile(r"AKIA[0-9A-Z]{16}"),              "AWS Access Key ID",              "CRITICAL"),
    (re.compile(r"AIza[0-9A-Za-z\-_]{35}"),       "Google API Key",                 "HIGH"),
    (re.compile(r"braintree[_\-]?(production|sandbox)[_\-]?[a-z0-9]{32}", re.IGNORECASE),
                                                    "Braintree API Key",             "CRITICAL"),
    (re.compile(r"razorpay[_\-]?(live|test)[_\-]?key[_\-]?secret[:\s=]+[a-zA-Z0-9]{20,}", re.IGNORECASE),
                                                    "Razorpay Key Secret",           "CRITICAL"),
]

# Insecure form / integration checks
_PLAINTEXT_CARD_FORM_PATTERN = re.compile(
    r'<input[^>]+(?:name|id)\s*=\s*["\'](?:card[_-]?number|cc[_-]?num|cardnum|creditcard|pan)["\']',
    re.IGNORECASE,
)

_MIXED_CONTENT_PATTERN = re.compile(r'<form[^>]+action\s*=\s*["\']http://', re.IGNORECASE)


class PaymentGatewayScanner(BaseScanner):
    MODULE_NAME = "payment_gateway"

    async def scan(self) -> List[VulnFinding]:
        findings: List[VulnFinding] = []

        try:
            resp = await self.client.get(self.target_url)
            body = resp.text
            content_type = resp.headers.get("content-type", "")
        except Exception as exc:
            self._log.debug("Could not fetch target for payment scan: %s", exc)
            return findings

        # 1. Card number patterns in page source / API response
        for pattern in _CARD_PATTERNS:
            matches = pattern.findall(body)
            for match in matches:
                if self._luhn_check(match):
                    findings.append(
                        self._finding(
                            title="Potential Credit Card Number Exposed in Response",
                            severity="CRITICAL",
                            description=(
                                f"A string matching a valid credit card number pattern was found in the HTTP response. "
                                f"If this is a real PAN, it constitutes a PCI-DSS violation."
                            ),
                            remediation=(
                                "Never include card numbers in API responses or HTML. "
                                "Mask PANs (show only last 4 digits). "
                                "Tokenise card data using your payment provider (Stripe, PayPal). "
                                "Conduct a PCI-DSS audit immediately."
                            ),
                            cwe_id="CWE-312",
                            cvss_score=9.8,
                            evidence=f"Matched pattern: {match[:4]}...{match[-4:]} (masked for safety)",
                            references=["https://www.pcisecuritystandards.org/"],
                        )
                    )
                    break  # One per pattern type

        # 2. Exposed secret/API keys for payment providers
        for pattern, label, severity in _SECRET_PATTERNS:
            m = pattern.search(body)
            if m:
                raw = m.group(0)
                masked = raw[:8] + "..." + raw[-4:] if len(raw) > 12 else raw[:4] + "..."
                findings.append(
                    self._finding(
                        title=f"Exposed Payment API Key: {label}",
                        severity=severity,
                        description=(
                            f"A {label} was found in the page source or API response. "
                            "Exposed keys allow attackers to make unauthorised charges, issue refunds, "
                            "or access customer payment data."
                        ),
                        remediation=(
                            "Immediately rotate/revoke the exposed key. "
                            "Never embed secret keys in client-side code or HTML. "
                            "Store secrets in environment variables or a secrets manager. "
                            "Check git history for previous leaks."
                        ),
                        cwe_id="CWE-798",
                        cvss_score=9.8 if severity == "CRITICAL" else 7.5,
                        evidence=f"Found: {masked}",
                        references=[
                            "https://stripe.com/docs/keys",
                            "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html",
                        ],
                    )
                )

        # 3. Plain-text card number form field (browser sends card directly to server)
        if _PLAINTEXT_CARD_FORM_PATTERN.search(body):
            findings.append(
                self._finding(
                    title="Card Number Collected via Plain HTML Form (Not via Payment SDK)",
                    severity="HIGH",
                    description=(
                        "An HTML input field with a name suggesting a card number was found. "
                        "If card data is submitted directly to your server, your application is in-scope for PCI-DSS SAQ D "
                        "and must meet the most rigorous compliance level."
                    ),
                    remediation=(
                        "Use a payment provider's hosted fields or JavaScript SDK (Stripe Elements, Braintree Drop-in UI). "
                        "This ensures card data never touches your server and reduces PCI scope to SAQ A."
                    ),
                    cwe_id="CWE-312",
                    cvss_score=7.5,
                    references=["https://stripe.com/docs/payments/elements"],
                )
            )

        # 4. Payment form submitting over HTTP (mixed content)
        if _MIXED_CONTENT_PATTERN.search(body):
            findings.append(
                self._finding(
                    title="Payment Form Action Uses Plain HTTP (Mixed Content)",
                    severity="CRITICAL",
                    description=(
                        "A form was found whose `action` attribute points to an HTTP URL. "
                        "Payment data submitted via this form will be transmitted in plaintext, "
                        "violating PCI-DSS Requirement 4.1."
                    ),
                    remediation=(
                        "Change the form action to an HTTPS URL. "
                        "Enable HSTS to prevent protocol downgrade attacks."
                    ),
                    cwe_id="CWE-319",
                    cvss_score=9.1,
                    references=["https://www.pcisecuritystandards.org/"],
                )
            )

        return findings

    # ------------------------------------------------------------------

    @staticmethod
    def _luhn_check(number: str) -> bool:
        """Return True if the number passes the Luhn algorithm."""
        digits = [int(d) for d in reversed(number) if d.isdigit()]
        if len(digits) < 13:
            return False
        total = 0
        for i, d in enumerate(digits):
            if i % 2 == 1:
                d *= 2
                if d > 9:
                    d -= 9
            total += d
        return total % 10 == 0