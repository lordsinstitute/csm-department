"""
VulnScan — Sensitive Data Exposure module.
Probes 30+ common paths for exposed config files, secrets, backups, and dev artefacts.
"""

from __future__ import annotations

from typing import List, Tuple

from backend.app.services.vulnscan.modules.base import BaseScanner
from backend.app.services.vulnscan.models import VulnFinding

# (path, title, severity, description_extra)
_PROBE_PATHS: List[Tuple[str, str, str, str]] = [
    # Environment / secrets
    ("/.env",                  "Exposed .env File",                    "CRITICAL", "Contains environment variables including DB credentials, API keys, and secrets."),
    ("/.env.local",            "Exposed .env.local File",              "CRITICAL", "Local environment overrides that may contain secrets."),
    ("/.env.production",       "Exposed .env.production File",         "CRITICAL", "Production secrets and configuration."),
    ("/.env.backup",           "Exposed .env Backup File",             "CRITICAL", "Backup of environment file that may contain secrets."),
    ("/.env.example",          "Exposed .env.example (Key Names Leak)","LOW",      "Reveals variable names attackers can search for in git history."),
    ("/config.json",           "Exposed config.json",                  "HIGH",     "Application configuration that may contain endpoints, credentials, or API keys."),
    ("/config.yml",            "Exposed config.yml",                   "HIGH",     "YAML config that may contain credentials."),
    ("/config.yaml",           "Exposed config.yaml",                  "HIGH",     "YAML config that may contain credentials."),
    ("/settings.py",           "Exposed settings.py (Django/Flask)",   "HIGH",     "Python settings file with SECRET_KEY, DB credentials, and other sensitive config."),
    ("/local_settings.py",     "Exposed local_settings.py",            "HIGH",     "Local Django settings override with potential secrets."),
    ("/application.yml",       "Exposed application.yml (Spring)",     "HIGH",     "Spring Boot config with DB and service credentials."),
    ("/appsettings.json",      "Exposed appsettings.json (.NET)",      "HIGH",     ".NET application settings with connection strings."),

    # Git / VCS
    ("/.git/config",           "Exposed Git Repository Config",        "CRITICAL", "Git config reveals remote URLs, author details. Combined with HEAD/COMMIT_EDITMSG can allow full source code download."),
    ("/.git/HEAD",             "Exposed Git HEAD",                     "HIGH",     "Confirms Git repository is accessible."),
    ("/.gitignore",            "Exposed .gitignore",                   "LOW",      "Reveals files intentionally excluded from version control — hints at sensitive paths."),
    ("/.svn/entries",          "Exposed SVN Repository",               "HIGH",     "SVN entries file accessible; source code may be downloadable."),

    # Database / SQL
    ("/dump.sql",              "Exposed SQL Database Dump",            "CRITICAL", "Full database dump accessible — likely contains all application data including credentials."),
    ("/backup.sql",            "Exposed SQL Backup",                   "CRITICAL", "SQL backup file accessible."),
    ("/db.sql",                "Exposed SQL File",                     "CRITICAL", "SQL file accessible."),
    ("/database.sql",          "Exposed SQL File (database.sql)",      "CRITICAL", "SQL file accessible."),

    # Debug / development
    ("/phpinfo.php",           "PHP Info Page Exposed",                "HIGH",     "phpinfo() reveals PHP version, loaded modules, configuration, and environment variables."),
    ("/info.php",              "PHP Info Page (info.php) Exposed",     "HIGH",     "phpinfo() page exposed."),
    ("/.DS_Store",             "Exposed .DS_Store File",               "MEDIUM",   "macOS metadata file that reveals directory structure."),
    ("/Thumbs.db",             "Exposed Thumbs.db File",               "LOW",      "Windows thumbnail cache revealing filenames in directory."),
    ("/web.config",            "Exposed web.config (.NET)",            "HIGH",     "IIS config with connection strings, auth settings, and encryption keys."),
    ("/crossdomain.xml",       "Exposed crossdomain.xml",              "MEDIUM",   "Flash cross-domain policy; overly permissive policy allows SWF attacks."),
    ("/clientaccesspolicy.xml","Exposed clientaccesspolicy.xml",       "MEDIUM",   "Silverlight cross-domain policy file."),

    # Cloud / infra
    ("/aws-credentials",       "Exposed AWS Credentials File",        "CRITICAL", "AWS access keys exposed."),
    ("/.aws/credentials",      "Exposed AWS Credentials Directory",   "CRITICAL", "AWS credentials file accessible."),
    ("/wp-config.php",         "Exposed WordPress Config",            "CRITICAL", "WordPress config with database host, username, password, and auth keys."),
    ("/wp-config.php.bak",     "Exposed WordPress Config Backup",     "CRITICAL", "Backup of WordPress config — plain text if backup served raw."),
    ("/sites/default/settings.php", "Exposed Drupal settings.php",   "CRITICAL", "Drupal configuration file with DB credentials."),

    # Backup files
    ("/backup.zip",            "Exposed ZIP Backup Archive",          "CRITICAL", "Source code or data backup accessible as a downloadable archive."),
    ("/backup.tar.gz",         "Exposed TAR Backup Archive",          "CRITICAL", "Backup archive accessible."),
    ("/site.tar.gz",           "Exposed Site Archive",                "CRITICAL", "Full site archive potentially downloadable."),
]

_SUCCESS_CODES = {200, 206}


class SensitiveDataScanner(BaseScanner):
    MODULE_NAME = "sensitive_data_exposure"

    async def scan(self) -> List[VulnFinding]:
        findings: List[VulnFinding] = []

        for path, title, severity, extra_desc in _PROBE_PATHS:
            url = f"{self.target_url}{path}"
            try:
                resp = await self.client.get(url)
                if resp.status_code not in _SUCCESS_CODES:
                    continue

                # Quick false-positive filter: if the body looks like an HTML page
                # (homepage returned for all 404s), skip it
                content_type = resp.headers.get("content-type", "")
                if "text/html" in content_type and len(resp.text) > 10_000:
                    # Large HTML response — likely a custom 404 page
                    continue

                # Check for non-trivial content
                if len(resp.content) < 10:
                    continue

                snippet = resp.text[:500].replace("\n", " ").strip()

                findings.append(
                    self._finding(
                        title=title,
                        severity=severity,
                        description=(
                            f"The path `{path}` returned HTTP {resp.status_code}. "
                            f"{extra_desc}"
                        ),
                        remediation=(
                            "Remove or restrict access to this path immediately. "
                            "Ensure web server configuration denies access to sensitive files. "
                            "Add these paths to your .gitignore and confirm they are not committed to version control."
                        ),
                        cwe_id="CWE-538",
                        cvss_score=9.1 if severity == "CRITICAL" else 7.5 if severity == "HIGH" else 5.3,
                        evidence=f"URL: {url}\nHTTP {resp.status_code}\nContent-Type: {content_type}\nSnippet: {snippet}",
                        affected_url=url,
                        references=[
                            "https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure",
                        ],
                    )
                )

            except Exception as exc:
                self._log.debug("Probe error for path '%s': %s", path, exc)

        return findings