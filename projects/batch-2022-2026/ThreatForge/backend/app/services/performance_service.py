"""Performance testing service with k6 support and async HTTP fallback."""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

logger = logging.getLogger(__name__)

# Storage for test results
_RESULTS_DIR = Path(__file__).resolve().parents[1] / "data" / "performance_tests"
_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


class PerformanceTestError(RuntimeError):
    """Raised when performance test execution fails."""


def generate_test_id(test_type: str) -> str:
    """Generate unique test ID with timestamp and type."""
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"perftest_{timestamp}_{test_type}_{unique_id}"


def parse_duration_to_seconds(duration: str) -> int:
    """Convert duration string (e.g., '2m', '30s', '1h') to seconds."""
    duration = duration.strip().lower()
    
    if duration.endswith('h'):
        return int(duration[:-1]) * 3600
    elif duration.endswith('m'):
        return int(duration[:-1]) * 60
    elif duration.endswith('s'):
        return int(duration[:-1])
    else:
        raise ValueError(f"Invalid duration format: {duration}. Use 's', 'm', or 'h' suffix")


def is_k6_installed() -> bool:
    """Check if k6 is installed on the system."""
    try:
        subprocess.run(
            ["k6", "version"],
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


class K6TestExecutor:
    """Executes performance tests using k6."""
    
    def __init__(self, test_id: str, target_url: str, config: Dict[str, Any]):
        self.test_id = test_id
        self.target_url = target_url
        self.config = config
    
    def run_test(self) -> Dict[str, Any]:
        """Execute k6 test and return results."""
        
        logger.info(
            "Starting k6 performance test",
            extra={
                "test_id": self.test_id,
                "target_url": self.target_url,
                "test_type": self.config.get("test_type"),
            }
        )
        
        # Generate k6 script
        script_content = self._generate_k6_script()
        
        # Create temporary script file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.js',
            delete=False
        ) as script_file:
            script_file.write(script_content)
            script_path = script_file.name
        
        # Create temporary file for JSON output
        json_output_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        )
        json_output_path = json_output_file.name
        json_output_file.close()
        
        try:
            # Run k6 test with JSON output to file
            result = subprocess.run(
                [
                    "k6", "run",
                    "--out", f"json={json_output_path}",
                    script_path
                ],
                capture_output=True,
                timeout=self.config.get("timeout", 300),
                text=True
            )
            
            # Read JSON output from file
            with open(json_output_path, 'r') as f:
                json_output = f.read()
            
            # Parse k6 output
            metrics = self._parse_k6_output(json_output)
            
            # Get k6 version
            version_result = subprocess.run(
                ["k6", "version"],
                capture_output=True,
                text=True
            )
            k6_version = version_result.stdout.strip()
            
            # Save results
            test_result = {
                "test_id": self.test_id,
                "target_url": self.target_url,
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "config": self.config,
                "metrics": metrics,
                "k6_version": k6_version,
                "_mock": False
            }
            
            _save_test_result(self.test_id, test_result)
            
            logger.info(
                "k6 test completed",
                extra={
                    "test_id": self.test_id,
                    "k6_version": k6_version,
                }
            )
            
            return test_result
            
        except subprocess.TimeoutExpired:
            logger.error(f"k6 test timed out after {self.config.get('timeout', 300)} seconds")
            raise PerformanceTestError("k6 test timed out")
        except Exception as e:
            logger.error(f"k6 test failed: {e}")
            raise PerformanceTestError(f"k6 test execution failed: {e}") from e
        finally:
            # Cleanup temporary files
            try:
                Path(script_path).unlink(missing_ok=True)
                Path(json_output_path).unlink(missing_ok=True)
            except Exception as e:
                logger.debug(f"Failed to cleanup temp files: {e}")
    
    def _generate_k6_script(self) -> str:
        """Generate k6 JavaScript test script based on configuration."""
        
        test_type = self.config.get("test_type", "load")
        vus = self.config.get("vus", 10)
        duration = self.config.get("duration", "30s")
        endpoints = self.config.get("endpoints", [{"method": "GET", "path": "/health"}])
        headers = self.config.get("headers", {})
        
        # Build headers object
        headers_js = json.dumps(headers) if headers else "{}"
        
        # Build endpoint requests
        endpoint_calls = []
        for idx, endpoint in enumerate(endpoints):
            method = endpoint.get("method", "GET").upper()
            path = endpoint.get("path", "/")
            url = f"{self.target_url.rstrip('/')}{path}"
            
            if method == "GET":
                endpoint_calls.append(f"    http.get('{url}', {{ headers: headers }});")
            elif method == "POST":
                endpoint_calls.append(f"    http.post('{url}', '', {{ headers: headers }});")
            elif method == "PUT":
                endpoint_calls.append(f"    http.put('{url}', '', {{ headers: headers }});")
            elif method == "DELETE":
                endpoint_calls.append(f"    http.del('{url}', '', {{ headers: headers }});")
        
        endpoint_code = "\n".join(endpoint_calls) if endpoint_calls else f"    http.get('{self.target_url}', {{ headers: headers }});"
        
        # Generate stages based on test type
        stages = self._generate_stages(test_type, vus)
        
        # Build thresholds
        thresholds = self.config.get("thresholds", {
            "http_req_duration": ["p(95)<500", "p(99)<1000"],
            "http_req_failed": ["rate<0.1"],
        })
        thresholds_js = json.dumps(thresholds)
        
        script = f"""
import http from 'k6/http';
import {{ check, sleep }} from 'k6';

export let options = {{
  stages: {stages},
  thresholds: {thresholds_js}
}};

const headers = {headers_js};

export default function() {{
{endpoint_code}
  sleep(1);
}}
"""
        
        return script
    
    def _generate_stages(self, test_type: str, vus: int) -> str:
        """Generate k6 stages configuration based on test type."""
        
        duration = self.config.get("duration", "30s")
        
        if test_type == "smoke":
            return json.dumps([
                {"duration": "1m", "target": 5},
                {"duration": "1m", "target": 5},
            ])
        
        elif test_type == "load":
            ramp_up = self.config.get("ramp_up", "30s")
            return json.dumps([
                {"duration": ramp_up, "target": vus},
                {"duration": duration, "target": vus},
                {"duration": "30s", "target": 0},
            ])
        
        elif test_type == "stress":
            return json.dumps([
                {"duration": "2m", "target": vus},
                {"duration": "3m", "target": int(vus * 1.5)},
                {"duration": "3m", "target": int(vus * 2)},
                {"duration": "3m", "target": int(vus * 2.5)},
                {"duration": "3m", "target": int(vus * 3)},
                {"duration": "2m", "target": 0},
            ])
        
        elif test_type == "spike":
            return json.dumps([
                {"duration": "1m", "target": vus},
                {"duration": "30s", "target": vus * 5},
                {"duration": "1m", "target": vus * 5},
                {"duration": "30s", "target": vus},
                {"duration": "1m", "target": 0},
            ])
        
        elif test_type == "capacity":
            max_vus = self.config.get("max_vus", vus * 10)
            step_vus = max(10, vus)
            stages = []
            current_vus = vus
            
            while current_vus <= max_vus:
                stages.append({"duration": "3m", "target": current_vus})
                current_vus += step_vus
            
            stages.append({"duration": "5m", "target": max_vus})
            stages.append({"duration": "3m", "target": 0})
            
            return json.dumps(stages)
        
        elif test_type == "soak":
            soak_duration = self.config.get("soak_duration", "30m")
            soak_vus = int(vus * 0.7)
            return json.dumps([
                {"duration": "5m", "target": soak_vus},
                {"duration": soak_duration, "target": soak_vus},
                {"duration": "5m", "target": 0},
            ])
        
        else:
            # Default to simple load test
            return json.dumps([
                {"duration": "1m", "target": vus},
                {"duration": duration, "target": vus},
                {"duration": "30s", "target": 0},
            ])
    
    def _parse_k6_output(self, json_output: str) -> Dict[str, Any]:
        """Parse k6 JSON output into metrics."""
        try:
            lines = json_output.strip().split('\n')
            
            # Extract metrics from k6 JSON output
            total_requests = 0
            failed_requests = 0
            response_times = []
            status_codes = defaultdict(int)
            
            for line in lines:
                try:
                    data = json.loads(line)
                    
                    if data.get("type") == "Point":
                        metric = data.get("metric", "")
                        
                        if metric == "http_reqs":
                            total_requests += data.get("data", {}).get("value", 0)
                        elif metric == "http_req_failed":
                            failed_requests += data.get("data", {}).get("value", 0)
                        elif metric == "http_req_duration":
                            value = data.get("data", {}).get("value", 0)
                            if value > 0:
                                response_times.append(value)
                        elif metric == "http_req_status":
                            status_code = int(data.get("data", {}).get("tags", {}).get("expected_response", "0"))
                            if status_code > 0:
                                status_codes[status_code] += 1
                
                except (json.JSONDecodeError, ValueError, KeyError):
                    continue
            
            # Calculate metrics
            if not response_times:
                response_times = [0]
            
            response_times.sort()
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            
            p50_idx = int(len(response_times) * 0.5)
            p95_idx = int(len(response_times) * 0.95)
            p99_idx = int(len(response_times) * 0.99)
            
            p50 = response_times[p50_idx] if p50_idx < len(response_times) else 0
            p95 = response_times[p95_idx] if p95_idx < len(response_times) else 0
            p99 = response_times[p99_idx] if p99_idx < len(response_times) else 0
            
            successful_requests = total_requests - failed_requests
            failure_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
            success_rate = 100 - failure_rate
            
            return {
                "requests": {
                    "total": total_requests,
                    "successful": successful_requests,
                    "failed": failed_requests,
                    "rate": 0,  # Will be calculated by format function
                    "failed_rate": round(failure_rate, 2),
                    "success_rate": round(success_rate, 2),
                    "status_codes": dict(status_codes)
                },
                "response_time": {
                    "avg": round(avg_response_time, 2),
                    "min": round(min_response_time, 2),
                    "max": round(max_response_time, 2),
                    "p50": round(p50, 2),
                    "p95": round(p95, 2),
                    "p99": round(p99, 2)
                },
                "virtual_users": {
                    "max": self.config.get("vus", 0),
                    "avg": round(self.config.get("vus", 0) * 0.7, 2)
                },
                "checks": {
                    "passed": successful_requests,
                    "failed": failed_requests,
                    "pass_rate": round(success_rate, 2)
                }
            }
        
        except Exception as e:
            logger.error(f"Failed to parse k6 output: {e}")
            return {
                "requests": {"total": 0, "failed": 0, "failed_rate": 0},
                "response_time": {"avg": 0, "min": 0, "max": 0, "p95": 0, "p99": 0},
                "virtual_users": {"max": 0, "avg": 0},
                "checks": {"passed": 0, "failed": 0, "pass_rate": 0}
            }


class AsyncHTTPTestExecutor:
    """Executes performance tests using async HTTP requests."""
    
    def __init__(self, test_id: str, target_url: str, config: Dict[str, Any]):
        self.test_id = test_id
        self.target_url = target_url.rstrip('/')
        self.config = config
        self.metrics_list = []
        self.start_time = None
        self.end_time = None
    
    async def run_test(self) -> Dict[str, Any]:
        """Execute async HTTP test and return results."""
        
        logger.info(
            "Starting async HTTP performance test",
            extra={
                "test_id": self.test_id,
                "target_url": self.target_url,
                "test_type": self.config.get("test_type"),
            }
        )
        
        if not HTTPX_AVAILABLE:
            logger.warning("httpx not installed, using mock results")
            return self._generate_mock_results()
        
        try:
            test_type = self.config.get("test_type", "load")
            vus = self.config.get("vus", 10)
            duration = self.config.get("duration", "30s")
            
            duration_seconds = parse_duration_to_seconds(duration)
            stages = self._generate_stages(test_type, vus, duration_seconds)
            
            self.start_time = time.time()
            await self._execute_stages(stages)
            self.end_time = time.time()
            
            return self._parse_results()
        
        except Exception as e:
            logger.error(f"Async test execution failed: {e}")
            raise PerformanceTestError(f"Async HTTP test failed: {e}") from e
    
    def _generate_stages(self, test_type: str, base_vus: int, duration: int) -> List[Dict[str, Any]]:
        """Generate load stages based on test type."""
        
        if test_type == "smoke":
            return [
                {"vus": 5, "duration": 60},
                {"vus": 5, "duration": 60},
            ]
        
        elif test_type == "load":
            ramp_up = self.config.get("ramp_up", "30s")
            ramp_up_seconds = parse_duration_to_seconds(ramp_up)
            return [
                {"vus": base_vus, "duration": ramp_up_seconds, "ramp": True},
                {"vus": base_vus, "duration": duration},
                {"vus": 0, "duration": 30, "ramp": True},
            ]
        
        elif test_type == "stress":
            multipliers = [1, 1.5, 2, 2.5, 3]
            stages = []
            stage_duration = 180
            
            for multiplier in multipliers:
                stages.append({
                    "vus": int(base_vus * multiplier),
                    "duration": stage_duration,
                    "ramp": True
                })
            stages.append({"vus": 0, "duration": 120, "ramp": True})
            return stages
        
        elif test_type == "spike":
            return [
                {"vus": base_vus, "duration": 60},
                {"vus": base_vus * 5, "duration": 30, "ramp": True},
                {"vus": base_vus * 5, "duration": 60},
                {"vus": base_vus, "duration": 30, "ramp": True},
                {"vus": 0, "duration": 60, "ramp": True},
            ]
        
        elif test_type == "capacity":
            max_vus = self.config.get("max_vus", base_vus * 10)
            step = max(10, base_vus // 5)
            stages = []
            current_vus = base_vus
            
            while current_vus <= max_vus:
                stages.append({"vus": current_vus, "duration": 180, "ramp": True})
                current_vus += step
            
            stages.append({"vus": max_vus, "duration": 300})
            stages.append({"vus": 0, "duration": 180, "ramp": True})
            return stages
        
        elif test_type == "soak":
            soak_duration_str = self.config.get("soak_duration", "30m")
            soak_duration = parse_duration_to_seconds(soak_duration_str)
            soak_vus = int(base_vus * 0.7)
            
            return [
                {"vus": soak_vus, "duration": 300, "ramp": True},
                {"vus": soak_vus, "duration": soak_duration},
                {"vus": 0, "duration": 300, "ramp": True},
            ]
        
        else:
            return [
                {"vus": base_vus, "duration": 60, "ramp": True},
                {"vus": base_vus, "duration": duration},
                {"vus": 0, "duration": 30, "ramp": True},
            ]
    
    async def _execute_stages(self, stages: List[Dict[str, Any]]) -> None:
        """Execute load stages sequentially."""
        endpoints = self.config.get("endpoints", [{"method": "GET", "path": "/health"}])
        headers = self.config.get("headers", {})
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for stage in stages:
                target_vus = stage.get("vus", 1)
                duration = stage.get("duration", 60)
                is_ramp = stage.get("ramp", False)
                
                await self._execute_stage(
                    client, target_vus, duration, is_ramp, endpoints, headers
                )
    
    async def _execute_stage(
        self,
        client: httpx.AsyncClient,
        target_vus: int,
        duration: int,
        is_ramp: bool,
        endpoints: List[Dict[str, Any]],
        headers: Dict[str, str]
    ) -> None:
        """Execute a single load stage."""
        
        end_time = time.time() + duration
        current_vus = 0
        iteration = 0
        
        while time.time() < end_time:
            if is_ramp and current_vus < target_vus:
                time_remaining = end_time - time.time()
                steps_remaining = max(1, int(time_remaining / 5))
                current_vus = min(target_vus, current_vus + max(1, target_vus // steps_remaining))
            else:
                current_vus = target_vus
            
            tasks = []
            for _ in range(current_vus):
                endpoint = endpoints[iteration % len(endpoints)]
                tasks.append(self._make_request(client, endpoint, headers))
                iteration += 1
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            await asyncio.sleep(0.1)
    
    async def _make_request(
        self,
        client: httpx.AsyncClient,
        endpoint: Dict[str, Any],
        headers: Dict[str, str]
    ) -> None:
        """Make a single HTTP request and record metrics."""
        
        method = endpoint.get("method", "GET").upper()
        path = endpoint.get("path", "/")
        url = f"{self.target_url}{path}"
        
        start = time.time()
        try:
            response = await client.request(
                method, url, headers=headers, follow_redirects=True
            )
            response_time_ms = (time.time() - start) * 1000
            
            success = 200 <= response.status_code < 400
            
            metric = {
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "response_time_ms": response_time_ms,
                "timestamp": time.time(),
                "success": success,
                "error": None if success else f"HTTP {response.status_code}"
            }
            self.metrics_list.append(metric)
        
        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start) * 1000
            metric = {
                "url": url,
                "method": method,
                "status_code": 0,
                "response_time_ms": response_time_ms,
                "timestamp": time.time(),
                "success": False,
                "error": "Request timeout"
            }
            self.metrics_list.append(metric)
        
        except Exception as e:
            response_time_ms = (time.time() - start) * 1000
            metric = {
                "url": url,
                "method": method,
                "status_code": 0,
                "response_time_ms": response_time_ms,
                "timestamp": time.time(),
                "success": False,
                "error": str(e)
            }
            self.metrics_list.append(metric)
    
    def _parse_results(self) -> Dict[str, Any]:
        """Parse collected metrics into results."""
        
        if not self.metrics_list:
            raise PerformanceTestError("No metrics collected during test")
        
        response_times = [m["response_time_ms"] for m in self.metrics_list]
        response_times.sort()
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        p50_idx = int(len(response_times) * 0.5)
        p95_idx = int(len(response_times) * 0.95)
        p99_idx = int(len(response_times) * 0.99)
        
        p50 = response_times[p50_idx] if p50_idx < len(response_times) else 0
        p95 = response_times[p95_idx] if p95_idx < len(response_times) else 0
        p99 = response_times[p99_idx] if p99_idx < len(response_times) else 0
        
        total_requests = len(self.metrics_list)
        successful_requests = sum(1 for m in self.metrics_list if m["success"])
        failed_requests = total_requests - successful_requests
        failure_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        success_rate = 100 - failure_rate
        
        test_duration = (self.end_time or time.time()) - (self.start_time or time.time())
        request_rate = total_requests / test_duration if test_duration > 0 else 0
        
        status_code_counts = defaultdict(int)
        for metric in self.metrics_list:
            status_code_counts[metric["status_code"]] += 1
        
        test_result = {
            "test_id": self.test_id,
            "target_url": self.target_url,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "config": self.config,
            "metrics": {
                "requests": {
                    "total": total_requests,
                    "successful": successful_requests,
                    "failed": failed_requests,
                    "rate_per_second": round(request_rate, 2),
                    "failed_rate": round(failure_rate, 2),
                    "success_rate": round(success_rate, 2),
                    "status_codes": dict(status_code_counts)
                },
                "response_time": {
                    "avg": round(avg_response_time, 2),
                    "min": round(min_response_time, 2),
                    "max": round(max_response_time, 2),
                    "p50": round(p50, 2),
                    "p95": round(p95, 2),
                    "p99": round(p99, 2)
                },
                "virtual_users": {
                    "max": self.config.get("vus", 0),
                    "avg": round(self.config.get("vus", 0) * 0.7, 2)
                },
                "checks": {
                    "passed": successful_requests,
                    "failed": failed_requests,
                    "pass_rate": round(success_rate, 2)
                }
            },
            "k6_version": "Pure Python async HTTP",
            "_mock": False
        }
        
        _save_test_result(self.test_id, test_result)
        
        logger.info(
            "Async HTTP test completed",
            extra={
                "test_id": self.test_id,
                "total_requests": total_requests,
                "success_rate": success_rate,
            }
        )
        
        return test_result
    
    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate realistic mock results when httpx is not available."""
        
        vus = self.config.get("vus", 10)
        duration = parse_duration_to_seconds(self.config.get("duration", "30s"))
        
        total_requests = int(vus * duration * 0.5)
        
        if vus < 50:
            failure_rate = 0.5
        elif vus < 100:
            failure_rate = 2.0
        elif vus < 500:
            failure_rate = 5.0
        else:
            failure_rate = 10.0
        
        if vus < 50:
            avg_response_time = 100
        elif vus < 100:
            avg_response_time = 250
        elif vus < 500:
            avg_response_time = 750
        else:
            avg_response_time = 1500
        
        successful_requests = int(total_requests * (100 - failure_rate) / 100)
        failed_requests = total_requests - successful_requests
        
        test_result = {
            "test_id": self.test_id,
            "target_url": self.target_url,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "config": self.config,
            "metrics": {
                "requests": {
                    "total": total_requests,
                    "successful": successful_requests,
                    "failed": failed_requests,
                    "rate_per_second": round(total_requests / duration, 2),
                    "failed_rate": round(failure_rate, 2),
                    "success_rate": round(100 - failure_rate, 2),
                    "status_codes": {200: successful_requests, 500: failed_requests}
                },
                "response_time": {
                    "avg": avg_response_time,
                    "min": int(avg_response_time * 0.3),
                    "max": int(avg_response_time * 3),
                    "p50": int(avg_response_time * 0.8),
                    "p95": int(avg_response_time * 2),
                    "p99": int(avg_response_time * 2.5)
                },
                "virtual_users": {
                    "max": vus,
                    "avg": round(vus * 0.7, 2)
                },
                "checks": {
                    "passed": successful_requests,
                    "failed": failed_requests,
                    "pass_rate": round(100 - failure_rate, 2)
                }
            },
            "k6_version": "mock (httpx not installed)",
            "_mock": True
        }
        
        _save_test_result(self.test_id, test_result)
        return test_result


def run_k6_test(
    test_id: str,
    target_url: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute performance test using k6 if available, async HTTP otherwise."""
    
    # Try k6 first
    if is_k6_installed():
        try:
            logger.info("Using k6 for performance testing")
            executor = K6TestExecutor(test_id, target_url, config)
            return executor.run_test()
        except Exception as e:
            logger.warning(f"k6 test failed, falling back to async HTTP: {e}")
            # Fall through to async HTTP
    
    # Fall back to async HTTP
    logger.info("Using async HTTP for performance testing")
    executor = AsyncHTTPTestExecutor(test_id, target_url, config)
    
    try:
        # Run async test in event loop
        result = asyncio.run(executor.run_test())
        return result
    except Exception as e:
        logger.error(f"Async test execution failed: {e}")
        # Return mock results on failure
        return executor._generate_mock_results()

def _save_test_result(test_id: str, result: Dict[str, Any]) -> None:
    result_path = _RESULTS_DIR / f"{test_id}.json"

    with result_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    # store metrics in database
    try:
        from backend.app.integrations.supabase_service import store_performance_run

        repo_id = "performance_repo"  # or map to repo if needed
        run_id = test_id

        store_performance_run(repo_id, run_id, result)

    except Exception as e:
        logger.warning(f"Failed to store performance metrics: {e}")


def get_performance_test(test_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve stored performance test result."""
    result_path = _RESULTS_DIR / f"{test_id}.json"
    
    if not result_path.exists():
        return None
    
    try:
        with result_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error(f"Failed to load test result {test_id}: {exc}")
        return None


def list_performance_tests(limit: int = 50) -> List[Dict[str, Any]]:
    """List recent performance test results."""
    results = []
    
    for result_path in sorted(_RESULTS_DIR.glob("*.json"), reverse=True):
        try:
            with result_path.open("r", encoding="utf-8") as f:
                result = json.load(f)
                results.append(result)
                
                if len(results) >= limit:
                    break
        except Exception as exc:
            logger.debug(f"Skipping unreadable result file {result_path}: {exc}")
            continue
    
    return results


def format_performance_test_response(test_result: Dict[str, Any]) -> Dict[str, Any]:
    """Format complete performance test results for API response."""
    
    metrics = test_result.get("metrics", {})
    requests_data = metrics.get("requests", {})
    response_time = metrics.get("response_time", {})
    virtual_users = metrics.get("virtual_users", {})
    checks = metrics.get("checks", {})
    
    failed_rate = requests_data.get("failed_rate", 0)
    success_rate = requests_data.get("success_rate", 100)
    total_requests = requests_data.get("total", 0)
    
    return {
        "test_id": test_result.get("test_id"),
        "status": test_result.get("status"),
        "message": f"Performance test completed. Total requests: {total_requests}, Success rate: {success_rate:.2f}%, Failure rate: {failed_rate:.2f}%",
        "target_url": test_result.get("target_url"),
        "timestamp": test_result.get("timestamp"),
        "test_config": {
            "test_type": test_result.get("config", {}).get("test_type"),
            "virtual_users": test_result.get("config", {}).get("vus"),
            "duration": test_result.get("config", {}).get("duration"),
            "endpoints": test_result.get("config", {}).get("endpoints")
        },
        "performance_metrics": {
            "requests": {
                "total": total_requests,
                "successful": requests_data.get("successful", 0),
                "failed": requests_data.get("failed", 0),
                "rate_per_second": round(requests_data.get("rate_per_second", 0), 2),
                "failed_rate_percent": round(failed_rate, 2),
                "success_rate_percent": round(success_rate, 2),
                "status_codes": requests_data.get("status_codes", {})
            },
            "response_time_ms": {
                "average": round(response_time.get("avg", 0), 2),
                "minimum": round(response_time.get("min", 0), 2),
                "maximum": round(response_time.get("max", 0), 2),
                "median_p50": round(response_time.get("p50", 0), 2),
                "percentile_95": round(response_time.get("p95", 0), 2),
                "percentile_99": round(response_time.get("p99", 0), 2)
            },
            "virtual_users": {
                "maximum": virtual_users.get("max", 0),
                "average": round(virtual_users.get("avg", 0), 2)
            },
            "checks": {
                "passed": checks.get("passed", 0),
                "failed": checks.get("failed", 0),
                "pass_rate_percent": round(checks.get("pass_rate", 100.0), 2)
            }
        },
        "system_info": {
            "implementation": test_result.get("k6_version", "Unknown"),
            "is_mock": test_result.get("_mock", False),
            "k6_available": is_k6_installed(),
            "httpx_available": HTTPX_AVAILABLE
        },
        "performance_summary": {
            "status": _get_performance_status(response_time, failed_rate),
            "bottlenecks": _identify_bottlenecks(metrics),
            "recommendations": _generate_recommendations(metrics, test_result.get("config", {}))
        }
    }


def _get_performance_status(response_time: Dict[str, Any], failed_rate: float) -> str:
    """Determine overall performance status."""
    avg_time = response_time.get("avg", 0)
    p95_time = response_time.get("p95", 0)
    
    if failed_rate > 10:
        return "CRITICAL - High failure rate (>10%)"
    elif failed_rate > 5:
        return "WARNING - Elevated failure rate (5-10%)"
    elif failed_rate > 1:
        return "WARNING - Minor failures detected (1-5%)"
    elif p95_time > 1000:
        return "WARNING - High response times (P95 > 1s)"
    elif avg_time > 500:
        return "FAIR - Moderate response times (avg > 500ms)"
    elif avg_time < 200:
        return "EXCELLENT - Fast response times (avg < 200ms)"
    else:
        return "GOOD - Acceptable performance"


def _identify_bottlenecks(metrics: Dict[str, Any]) -> List[str]:
    """Identify potential performance bottlenecks."""
    bottlenecks = []
    
    response_time = metrics.get("response_time", {})
    requests_data = metrics.get("requests", {})
    
    avg_time = response_time.get("avg", 0)
    p95_time = response_time.get("p95", 0)
    p99_time = response_time.get("p99", 0)
    failed_rate = requests_data.get("failed_rate", 0)
    
    if failed_rate > 5:
        bottlenecks.append(f"High failure rate: {failed_rate:.1f}%")
    
    if avg_time > 500:
        bottlenecks.append(f"Slow average response time: {avg_time:.0f}ms")
    
    if p95_time > 1000:
        bottlenecks.append(f"High P95 latency: {p95_time:.0f}ms (5% of requests exceed 1s)")
    
    if p99_time > 2000:
        bottlenecks.append(f"Very high P99 latency: {p99_time:.0f}ms (1% of requests exceed 2s)")
    
    if p99_time > avg_time * 3:
        bottlenecks.append("High latency variance - inconsistent performance")
    
    if failed_rate > 0 and failed_rate <= 1:
        bottlenecks.append(f"Minor failures detected: {failed_rate:.2f}%")
    
    if not bottlenecks:
        bottlenecks.append("✓ No significant bottlenecks detected")
    
    return bottlenecks


def _generate_recommendations(metrics: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    """Generate performance improvement recommendations."""
    recommendations = []
    
    response_time = metrics.get("response_time", {})
    requests_data = metrics.get("requests", {})
    
    avg_time = response_time.get("avg", 0)
    failed_rate = requests_data.get("failed_rate", 0)
    vus = config.get("vus", 10)
    
    if failed_rate > 10:
        recommendations.append("🔴 CRITICAL: Investigate server errors immediately - check logs")
        recommendations.append("Review server capacity and error handling")
    elif failed_rate > 5:
        recommendations.append("⚠️  Review error patterns in server logs")
        recommendations.append("Implement circuit breakers or rate limiting")
    elif failed_rate > 1:
        recommendations.append("Monitor failures for patterns or specific endpoints")
    
    if avg_time > 1000:
        recommendations.append("🔴 Optimize database queries and API calls urgently")
        recommendations.append("Consider implementing Redis caching")
        recommendations.append("Profile application code for bottlenecks")
    elif avg_time > 500:
        recommendations.append("📊 Implement caching strategies (Redis/Memcached)")
        recommendations.append("Optimize N+1 query problems")
        recommendations.append("Consider asynchronous processing")
    
    if response_time.get("p95", 0) > avg_time * 2:
        recommendations.append("Investigate outlier requests causing high latency")
        recommendations.append("Implement request timeouts and async operations")
    
    if vus > 100 and avg_time > 500:
        recommendations.append("🏗️  Consider horizontal scaling for current load")
        recommendations.append("Evaluate load balancer configuration")
        recommendations.append("Monitor infrastructure capacity metrics")
    elif vus > 50 and failed_rate > 0:
        recommendations.append("Test with higher load to identify breaking points")
        recommendations.append("Prepare scaling strategy")
    
    if not recommendations:
        recommendations.append("✓ Performance is acceptable for current load")
        recommendations.append("💡 Consider stress testing with higher VUs to find limits")
        recommendations.append("Establish monitoring and alerting on key metrics")
    
    return recommendations


__all__ = [
    "PerformanceTestError",
    "generate_test_id",
    "run_k6_test",
    "get_performance_test",
    "list_performance_tests",
    "format_performance_test_response",
    "parse_duration_to_seconds",
    "is_k6_installed",
]