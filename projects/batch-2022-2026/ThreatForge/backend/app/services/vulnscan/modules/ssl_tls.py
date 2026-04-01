"""
VulnScan — SSL/TLS module.
Inspects TLS certificate validity, protocol versions, and cipher suites.
Uses Python's ssl stdlib for low-level checks without needing external tools.
"""

from __future__ import annotations

import datetime
import socket
import ssl
from typing import List
from urllib.parse import urlparse

from backend.app.services.vulnscan.modules.base import BaseScanner
from backend.app.services.vulnscan.models import VulnFinding

# Cipher suites considered weak / deprecated
_WEAK_CIPHERS = {
    "RC4", "DES", "3DES", "NULL", "EXPORT", "ADH", "AECDH",
    "MD5", "SHA1", "CBC",
}

# Protocol versions that should be rejected
_DEPRECATED_PROTOCOLS = {
    ssl.TLSVersion.TLSv1,
    ssl.TLSVersion.TLSv1_1,
}

# Days before expiry to flag as WARNING
_EXPIRY_WARNING_DAYS = 30
_EXPIRY_CRITICAL_DAYS = 7


class SSLTLSScanner(BaseScanner):
    MODULE_NAME = "ssl_tls"

    async def scan(self) -> List[VulnFinding]:
        findings: List[VulnFinding] = []
        parsed = urlparse(self.target_url)
        hostname = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)

        if parsed.scheme != "https":
            findings.append(
                self._finding(
                    title="Site Does Not Use HTTPS",
                    severity="HIGH",
                    description="The target URL uses plain HTTP. All communication is unencrypted, exposing credentials, session tokens, and sensitive data to interception.",
                    remediation="Redirect all HTTP traffic to HTTPS. Obtain a valid TLS certificate from a trusted CA (e.g. Let's Encrypt).",
                    cwe_id="CWE-319",
                    cvss_score=7.5,
                    references=["https://letsencrypt.org/", "https://owasp.org/www-project-transport-layer-protection-cheat-sheet/"],
                )
            )
            return findings

        # ---------- certificate checks ----------
        cert_info = self._fetch_cert(hostname, port)
        if cert_info is None:
            findings.append(
                self._finding(
                    title="TLS Handshake Failed",
                    severity="HIGH",
                    description="Could not complete a TLS handshake with the target. The server may have an invalid or missing certificate.",
                    remediation="Ensure the server presents a valid, trusted TLS certificate and supports modern TLS versions.",
                    cwe_id="CWE-295",
                    cvss_score=7.5,
                )
            )
            return findings

        cert, protocol, cipher = cert_info

        # Self-signed / untrusted
        if self._is_self_signed(cert):
            findings.append(
                self._finding(
                    title="Self-Signed TLS Certificate Detected",
                    severity="HIGH",
                    description="The server presents a self-signed certificate not issued by a trusted Certificate Authority. Browsers will warn users, and connections are susceptible to MitM attacks.",
                    remediation="Replace the self-signed certificate with one issued by a trusted CA such as Let's Encrypt.",
                    cwe_id="CWE-295",
                    cvss_score=7.4,
                    evidence=f"Issuer: {cert.get('issuer')}",
                    references=["https://letsencrypt.org/"],
                )
            )

        # Expiry checks
        expiry_findings = self._check_expiry(cert)
        findings.extend(expiry_findings)

        # Hostname mismatch — ssl.match_hostname was removed in Python 3.12
        if not self._hostname_matches(cert, hostname):
            findings.append(
                self._finding(
                    title="TLS Certificate Hostname Mismatch",
                    severity="HIGH",
                    description=f"The certificate's Common Name / SAN does not match the hostname '{hostname}'. This could indicate a misconfiguration or a MitM attack.",
                    remediation="Obtain a certificate that includes the correct hostname as a Subject Alternative Name.",
                    cwe_id="CWE-297",
                    cvss_score=7.4,
                    evidence=f"Hostname: {hostname}, Cert SANs: {cert.get('subjectAltName')}",
                )
            )

        # ---------- protocol version ----------
        if protocol in ("TLSv1", "TLSv1.1", "SSLv2", "SSLv3"):
            findings.append(
                self._finding(
                    title=f"Deprecated TLS Protocol Version ({protocol})",
                    severity="HIGH",
                    description=f"The server negotiated {protocol}, which is deprecated and known to contain cryptographic weaknesses (e.g. POODLE, BEAST). Modern clients may refuse to connect.",
                    remediation="Disable TLS 1.0 and 1.1 in server configuration. Support TLS 1.2 and TLS 1.3 only.",
                    cwe_id="CWE-326",
                    cvss_score=7.4,
                    evidence=f"Negotiated protocol: {protocol}",
                    references=["https://tools.ietf.org/html/rfc8996"],
                )
            )

        # ---------- weak cipher ----------
        if cipher:
            cipher_name = cipher[0] if isinstance(cipher, tuple) else str(cipher)
            for weak in _WEAK_CIPHERS:
                if weak in cipher_name.upper():
                    findings.append(
                        self._finding(
                            title=f"Weak TLS Cipher Suite Negotiated ({cipher_name})",
                            severity="MEDIUM",
                            description=f"The negotiated cipher suite '{cipher_name}' uses a weak or deprecated algorithm ({weak}). This may allow decryption of captured traffic.",
                            remediation="Configure the server to prefer strong cipher suites (AES-GCM, ChaCha20) and disable weak ones.",
                            cwe_id="CWE-326",
                            cvss_score=5.9,
                            evidence=f"Cipher suite: {cipher_name}",
                        )
                    )
                    break

        return findings

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_cert(self, hostname: str, port: int):
        """Attempt a TLS handshake and return (cert_dict, protocol, cipher) or None."""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE  # We verify manually

        try:
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    protocol = ssock.version()
                    cipher = ssock.cipher()
                    return cert, protocol, cipher
        except Exception as exc:
            self._log.debug("TLS connection failed for %s:%s — %s", hostname, port, exc)
            return None

    def _hostname_matches(self, cert: dict, hostname: str) -> bool:
        """Check hostname against cert SANs or CN. Replaces ssl.match_hostname (removed in Python 3.12)."""
        import fnmatch
        sans = cert.get("subjectAltName", [])
        for typ, value in sans:
            if typ == "DNS":
                if fnmatch.fnmatch(hostname.lower(), value.lower()):
                    return True
        # Fall back to CN if no SANs present
        if not sans:
            subject = dict(x[0] for x in cert.get("subject", []))
            cn = subject.get("commonName", "")
            if fnmatch.fnmatch(hostname.lower(), cn.lower()):
                return True
        return False

    def _is_self_signed(self, cert: dict) -> bool:
        """Return True if the issuer equals the subject (self-signed)."""
        issuer = dict(x[0] for x in cert.get("issuer", []))
        subject = dict(x[0] for x in cert.get("subject", []))
        return issuer.get("commonName") == subject.get("commonName")

    def _check_expiry(self, cert: dict) -> List[VulnFinding]:
        findings = []
        not_after_str = cert.get("notAfter")
        if not not_after_str:
            return findings

        try:
            expiry = datetime.datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
            now = datetime.datetime.utcnow()
            days_left = (expiry - now).days
        except ValueError:
            return findings

        if days_left < 0:
            findings.append(
                self._finding(
                    title="TLS Certificate Has Expired",
                    severity="CRITICAL",
                    description=f"The TLS certificate expired {abs(days_left)} day(s) ago. Browsers will block access and display a security warning to all users.",
                    remediation="Renew the TLS certificate immediately. Consider enabling auto-renewal (e.g. Certbot with Let's Encrypt).",
                    cwe_id="CWE-298",
                    cvss_score=9.1,
                    evidence=f"Certificate expiry: {not_after_str}",
                )
            )
        elif days_left <= _EXPIRY_CRITICAL_DAYS:
            findings.append(
                self._finding(
                    title=f"TLS Certificate Expiring in {days_left} Day(s) — Critical",
                    severity="HIGH",
                    description=f"The TLS certificate will expire in {days_left} day(s). Imminent expiry will cause browsers to block the site.",
                    remediation="Renew the certificate now. Enable auto-renewal to prevent recurrence.",
                    cwe_id="CWE-298",
                    cvss_score=7.5,
                    evidence=f"Certificate expiry: {not_after_str}",
                )
            )
        elif days_left <= _EXPIRY_WARNING_DAYS:
            findings.append(
                self._finding(
                    title=f"TLS Certificate Expiring Soon ({days_left} Days Remaining)",
                    severity="MEDIUM",
                    description=f"The TLS certificate expires in {days_left} days. Schedule renewal to avoid service interruption.",
                    remediation="Renew the certificate within the next few days.",
                    cwe_id="CWE-298",
                    cvss_score=4.0,
                    evidence=f"Certificate expiry: {not_after_str}",
                )
            )

        return findings