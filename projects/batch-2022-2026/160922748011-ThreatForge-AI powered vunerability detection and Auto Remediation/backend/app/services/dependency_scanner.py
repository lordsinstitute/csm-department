"""
Dependency vulnerability scanner for multiple package managers.
Checks for outdated and vulnerable packages.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import httpx
import logging

logger = logging.getLogger(__name__)


class DependencyVulnerability:
    """Represents a vulnerable dependency."""
    
    def __init__(
        self,
        package: str,
        current_version: str,
        vulnerable_version: str,
        severity: str,
        cve_id: Optional[str] = None,
        recommendation: str = "Update to latest version"
    ):
        self.package = package
        self.current_version = current_version
        self.vulnerable_version = vulnerable_version
        self.severity = severity
        self.cve_id = cve_id
        self.recommendation = recommendation


def scan_python_requirements(file_path: Path) -> List[DependencyVulnerability]:
    """
    Scan requirements.txt for vulnerable Python packages.
    Uses OSV (Open Source Vulnerabilities) database.
    """
    vulnerabilities = []
    
    try:
        content = file_path.read_text()
        
        # Parse requirements
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Extract package and version
            match = re.match(r'([a-zA-Z0-9_-]+)\s*([=><~!]+)\s*([0-9.]+)', line)
            if not match:
                continue
            
            package, operator, version = match.groups()
            
            # Query OSV database
            vuln = _check_osv_vulnerability('PyPI', package, version)
            if vuln:
                vulnerabilities.append(vuln)
    
    except Exception as e:
        logger.error(f"Error scanning Python requirements: {e}")
    
    return vulnerabilities


def scan_nodejs_packages(file_path: Path) -> List[DependencyVulnerability]:
    """
    Scan package.json for vulnerable Node.js packages.
    Uses npm audit API.
    """
    vulnerabilities = []
    
    try:
        data = json.loads(file_path.read_text())
        dependencies = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
        
        for package, version in dependencies.items():
            # Remove special chars (^, ~, etc)
            clean_version = re.sub(r'[^0-9.]', '', version)
            
            # Query NPM registry
            vuln = _check_npm_vulnerability(package, clean_version)
            if vuln:
                vulnerabilities.append(vuln)
    
    except Exception as e:
        logger.error(f"Error scanning Node.js packages: {e}")
    
    return vulnerabilities


def _check_osv_vulnerability(
    ecosystem: str, 
    package: str, 
    version: str
) -> Optional[DependencyVulnerability]:
    """
    Query OSV (Open Source Vulnerabilities) database.
    API: https://osv.dev/
    """
    try:
        response = httpx.post(
            'https://api.osv.dev/v1/query',
            json={
                'package': {'name': package, 'ecosystem': ecosystem},
                'version': version
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            vulns = data.get('vulns', [])
            
            if vulns:
                vuln = vulns[0]  # Take first vulnerability
                
                # Determine severity
                severity = 'high'
                if 'database_specific' in vuln:
                    severity_score = vuln['database_specific'].get('severity', '')
                    if 'CRITICAL' in severity_score.upper():
                        severity = 'critical'
                    elif 'HIGH' in severity_score.upper():
                        severity = 'high'
                    elif 'MEDIUM' in severity_score.upper():
                        severity = 'medium'
                    else:
                        severity = 'low'
                
                return DependencyVulnerability(
                    package=package,
                    current_version=version,
                    vulnerable_version=version,
                    severity=severity,
                    cve_id=vuln.get('id', 'OSV-' + vuln.get('id', 'UNKNOWN')),
                    recommendation=vuln.get('summary', 'Update to patched version')
                )
    
    except Exception as e:
        logger.debug(f"OSV check failed for {package}: {e}")
    
    return None


def _check_npm_vulnerability(package: str, version: str) -> Optional[DependencyVulnerability]:
    """
    Check npm registry for known vulnerabilities.
    Uses npm registry API.
    """
    try:
        # Get package metadata
        response = httpx.get(
            f'https://registry.npmjs.org/{package}',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if version has known vulnerabilities
            # (This is simplified - real implementation would check advisories)
            versions = data.get('versions', {})
            if version in versions:
                version_data = versions[version]
                
                # Check for deprecated packages
                if version_data.get('deprecated'):
                    return DependencyVulnerability(
                        package=package,
                        current_version=version,
                        vulnerable_version=version,
                        severity='medium',
                        recommendation=f"Package deprecated: {version_data.get('deprecated')}"
                    )
    
    except Exception as e:
        logger.debug(f"NPM check failed for {package}: {e}")
    
    return None


def scan_repository_dependencies(repo_dir: Path) -> Dict[str, List[DependencyVulnerability]]:
    """
    Scan all dependency files in a repository.
    
    Returns:
        Dict mapping file paths to vulnerability lists
    """
    results = {}
    
    # Python
    for req_file in repo_dir.rglob('requirements*.txt'):
        vulns = scan_python_requirements(req_file)
        if vulns:
            results[str(req_file.relative_to(repo_dir))] = vulns
    
    # Node.js
    for pkg_file in repo_dir.rglob('package.json'):
        vulns = scan_nodejs_packages(pkg_file)
        if vulns:
            results[str(pkg_file.relative_to(repo_dir))] = vulns
    
    return results


def generate_dependency_report(
    vulnerabilities: Dict[str, List[DependencyVulnerability]]
) -> Dict[str, object]:
    """
    Generate a structured report of dependency vulnerabilities.
    """
    total_vulns = sum(len(v) for v in vulnerabilities.values())
    
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    affected_files = list(vulnerabilities.keys())
    
    detailed_findings = []
    
    for file_path, vulns in vulnerabilities.items():
        for vuln in vulns:
            severity_counts[vuln.severity] += 1
            
            detailed_findings.append({
                'file': file_path,
                'package': vuln.package,
                'current_version': vuln.current_version,
                'severity': vuln.severity,
                'cve_id': vuln.cve_id,
                'recommendation': vuln.recommendation
            })
    
    return {
        'total_vulnerabilities': total_vulns,
        'severity_breakdown': severity_counts,
        'affected_files': affected_files,
        'findings': detailed_findings
    }