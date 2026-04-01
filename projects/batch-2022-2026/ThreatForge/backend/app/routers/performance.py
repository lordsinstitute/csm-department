"""API endpoints for performance testing functionality."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, HttpUrl
from backend.app.services.performance_service import format_performance_test_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/performance", tags=["performance"])


class PerformanceTestRequest(BaseModel):
    """Request to start a performance test."""
    
    target_url: HttpUrl = Field(
        ...,
        description="The URL to test (must be publicly accessible)",
        examples=["https://api.example.com"]
    )
    
    test_type: str = Field(
        default="load",
        description="Type of performance test to run",
        pattern="^(load|stress|spike|capacity|soak|smoke)$"
    )
    
    vus: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Number of virtual users (concurrent connections) for base load"
    )
    
    duration: str = Field(
        default="30s",
        description="Test duration (e.g., '30s', '2m', '1h')",
        pattern=r"^\d+[smh]$"
    )
    
    ramp_up: Optional[str] = Field(
        default=None,
        description="Ramp-up time to reach target VUs (for load test)",
        pattern=r"^\d+[smh]$"
    )
    
    max_vus: Optional[int] = Field(
        default=None,
        ge=1,
        le=5000,
        description="Maximum VUs for capacity test"
    )
    
    soak_duration: Optional[str] = Field(
        default=None,
        description="Duration for soak test (e.g., '30m', '2h')",
        pattern=r"^\d+[smh]$"
    )
    
    endpoints: List[Dict[str, Any]] = Field(
        default=[{"method": "GET", "path": "/health"}],
        description="List of endpoints to test with their HTTP methods"
    )
    
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom HTTP headers to include in requests"
    )
    
    thresholds: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="Custom performance thresholds"
    )


class PerformanceTestResponse(BaseModel):
    """Response when test is started."""
    
    test_id: str = Field(..., description="Unique test identifier")
    status: str = Field(..., description="Test status")
    message: str = Field(..., description="Human-readable message")
    target_url: str = Field(..., description="URL being tested")


class PerformanceTestResult(BaseModel):
    """Performance test results."""
    
    test_id: str
    target_url: str
    status: str
    timestamp: str
    config: Dict[str, Any]
    metrics: Dict[str, Any]
    k6_version: Optional[str] = None


@router.post("/test")
async def start_performance_test(request: PerformanceTestRequest) -> PerformanceTestResponse:
    """
    Start a performance test on the specified URL.
    
    This endpoint uses k6 (https://k6.io) to perform various types of load testing.
    
    **Test Types:**
    
    1. **load** (default): Standard load test with gradual ramp-up
       - Ramps up to target VUs
       - Maintains steady load
       - Gracefully ramps down
       - Best for: Normal capacity testing
    
    2. **stress**: Progressive load increase to find breaking point
       - Starts at normal load
       - Increases in stages (1.5x, 2x, 2.5x, 3x)
       - Identifies system limits
       - Best for: Finding maximum capacity before failure
    
    3. **spike**: Sudden traffic surge testing
       - Normal load baseline
       - Sudden 5x spike
       - Tests recovery
       - Best for: Black Friday, viral content scenarios
    
    4. **capacity**: Gradual increase to find optimal capacity
       - Incremental load increases
       - Sustained peak testing
       - Best for: Infrastructure planning
    
    5. **soak**: Extended duration at moderate load
       - 70% capacity for extended period (30min default)
       - Detects memory leaks and degradation
       - Best for: Stability validation
    
    6. **smoke**: Quick validation with minimal load
       - 5 VUs for 2 minutes
       - Verifies basic functionality
       - Best for: CI/CD quick checks
    
    **Example Requests:**
    
    Load Test:
    ```json
    {
        "target_url": "https://api.example.com",
        "test_type": "load",
        "vus": 50,
        "duration": "2m",
        "ramp_up": "30s"
    }
    ```
    
    Stress Test:
    ```json
    {
        "target_url": "https://api.example.com",
        "test_type": "stress",
        "vus": 100
    }
    ```
    
    Spike Test:
    ```json
    {
        "target_url": "https://api.example.com",
        "test_type": "spike",
        "vus": 50
    }
    ```
    
    **Requirements:**
    - k6 must be installed on the server
    - Target URL must be publicly accessible
    """
    from backend.app.services.performance_service import (
        generate_test_id,
        run_k6_test,
        PerformanceTestError,
    )
    
    test_type = request.test_type.lower()
    
    logger.info(
        "Performance test requested",
        extra={
            "target_url": str(request.target_url),
            "test_type": test_type,
            "vus": request.vus,
            "duration": request.duration,
        }
    )
    
    # Generate unique test ID with test type
    test_id = generate_test_id(test_type)
    
    # Build test configuration
    test_config = {
        "test_type": test_type,
        "vus": request.vus,
        "duration": request.duration,
        "endpoints": request.endpoints,
        "headers": request.headers,
    }
    
    # Add optional parameters based on test type
    if request.ramp_up and test_type == "load":
        test_config["ramp_up"] = request.ramp_up
    
    if request.max_vus and test_type == "capacity":
        test_config["max_vus"] = request.max_vus
    
    if request.soak_duration and test_type == "soak":
        test_config["soak_duration"] = request.soak_duration
    
    if request.thresholds:
        test_config["thresholds"] = request.thresholds
    
    # Estimate test duration for timeout
    timeout = _estimate_test_timeout(test_type, test_config)
    test_config["timeout"] = timeout
    
    try:
        # Run k6 test in background thread
        result = await run_in_threadpool(
            run_k6_test,
            test_id,
            str(request.target_url),
            test_config
        )
        
        logger.info(
            "Performance test completed",
            extra={
                "test_id": test_id,
                "test_type": test_type,
                "status": result.get("status"),
            }
        )
        
        formatted = format_performance_test_response(result)
        return formatted
        
    except PerformanceTestError as exc:
        logger.error(
            "Performance test failed",
            extra={"test_id": test_id, "test_type": test_type, "error": str(exc)}
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"{test_type.capitalize()} test failed",
                "details": str(exc),
                "test_id": test_id
            }
        ) from exc
    
    except Exception as exc:
        logger.exception(
            "Unexpected error during performance test",
            extra={"test_id": test_id, "test_type": test_type}
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unexpected error during performance test",
                "details": str(exc)
            }
        ) from exc


def _estimate_test_timeout(test_type: str, config: Dict[str, Any]) -> int:
    """Estimate appropriate timeout for test based on type and config."""
    base_timeouts = {
        "smoke": 180,      # 3 minutes
        "load": 300,       # 5 minutes
        "spike": 420,      # 7 minutes
        "stress": 1200,    # 20 minutes
        "capacity": 1800,  # 30 minutes
        "soak": 3600,      # 60 minutes (can be longer)
    }
    
    timeout = base_timeouts.get(test_type, 300)
    
    # Add buffer for soak tests based on duration
    if test_type == "soak" and "soak_duration" in config:
        duration_str = config["soak_duration"]
        # Parse duration (e.g., "30m" -> 1800 seconds)
        import re
        match = re.match(r"(\d+)([smh])", duration_str)
        if match:
            value, unit = int(match.group(1)), match.group(2)
            multipliers = {"s": 1, "m": 60, "h": 3600}
            duration_seconds = value * multipliers.get(unit, 60)
            timeout = duration_seconds + 600  # Add 10 min buffer
    
    return timeout


@router.get("/test/{test_id}", response_model=PerformanceTestResult)
async def get_performance_test_result(test_id: str) -> PerformanceTestResult:
    """
    Retrieve results for a specific performance test.
    
    Returns detailed metrics including:
    - Total requests and request rate
    - Response time statistics (avg, min, max, percentiles)
    - Virtual user metrics
    - Check pass/fail rates
    - Error rates
    
    **Example Response:**
    ```json
    {
        "test_id": "perftest_20240122T143045_a1b2c3d4",
        "target_url": "https://api.example.com",
        "status": "completed",
        "timestamp": "2024-01-22T14:30:45.123Z",
        "metrics": {
            "requests": {
                "total": 1500,
                "rate": 25.0,
                "failed_rate": 2.3
            },
            "response_time": {
                "avg": 245.6,
                "p95": 487.2,
                "p99": 612.8
            }
        }
    }
    ```
    """
    from backend.app.services.performance_service import get_performance_test
    
    logger.info("Performance test result requested", extra={"test_id": test_id})
    
    result = await run_in_threadpool(get_performance_test, test_id)
    
    if not result:
        logger.warning("Performance test not found", extra={"test_id": test_id})
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Performance test not found",
                "test_id": test_id
            }
        )
    
    return PerformanceTestResult(**result)


@router.get("/tests", response_model=List[PerformanceTestResult])
async def list_performance_tests(limit: int = 50) -> List[PerformanceTestResult]:
    """
    List recent performance tests.
    
    Returns a list of test results sorted by timestamp (newest first).
    Useful for displaying test history and comparing performance over time.
    
    **Query Parameters:**
    - `limit`: Maximum number of tests to return (default: 50, max: 100)
    """
    from backend.app.services.performance_service import list_performance_tests as list_tests
    
    # Validate limit
    if limit < 1:
        limit = 50
    elif limit > 100:
        limit = 100
    
    logger.info("Listing performance tests", extra={"limit": limit})
    
    tests = await run_in_threadpool(list_tests, limit)
    
    return [PerformanceTestResult(**test) for test in tests]


@router.get("/metrics/aggregate")
async def get_aggregate_metrics(target_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Get aggregated performance metrics across multiple tests.
    
    Optionally filter by target URL to see metrics for a specific endpoint.
    
    **Returns:**
    - Average response times across all tests
    - Request rates and throughput trends
    - Error rate trends
    - Capacity recommendations
    """
    from backend.app.services.performance_service import list_performance_tests as list_tests
    
    logger.info("Aggregate metrics requested", extra={"target_url": target_url})
    
    tests = await run_in_threadpool(list_tests, 100)
    
    # Filter by target URL if specified
    if target_url:
        tests = [t for t in tests if t.get("target_url") == target_url]
    
    if not tests:
        return {
            "total_tests": 0,
            "message": "No performance tests found"
        }
    
    # Calculate aggregate metrics
    total_requests = sum(
        t.get("metrics", {}).get("requests", {}).get("total", 0)
        for t in tests
    )
    
    avg_response_times = [
        t.get("metrics", {}).get("response_time", {}).get("avg", 0)
        for t in tests
        if t.get("metrics", {}).get("response_time", {}).get("avg", 0) > 0
    ]
    
    avg_error_rates = [
        t.get("metrics", {}).get("requests", {}).get("failed_rate", 0)
        for t in tests
    ]
    
    max_vus = [
        t.get("metrics", {}).get("virtual_users", {}).get("max", 0)
        for t in tests
    ]
    
    return {
        "total_tests": len(tests),
        "target_url": target_url,
        "aggregate_metrics": {
            "total_requests": total_requests,
            "avg_response_time": round(sum(avg_response_times) / len(avg_response_times), 2) if avg_response_times else 0,
            "avg_error_rate": round(sum(avg_error_rates) / len(avg_error_rates), 2) if avg_error_rates else 0,
            "max_concurrent_users": max(max_vus) if max_vus else 0,
            "tests_analyzed": len(tests)
        },
        "recommendations": _generate_capacity_recommendations(tests)
    }


def _generate_capacity_recommendations(tests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate capacity recommendations based on test results."""
    
    if not tests:
        return {"message": "Insufficient data for recommendations"}
    
    # Find test with best performance
    best_test = max(
        tests,
        key=lambda t: (
            t.get("metrics", {}).get("requests", {}).get("total", 0) /
            max(t.get("metrics", {}).get("response_time", {}).get("avg", 1), 1)
        )
    )
    
    best_vus = best_test.get("metrics", {}).get("virtual_users", {}).get("max", 0)
    best_avg_response = best_test.get("metrics", {}).get("response_time", {}).get("avg", 0)
    
    # Calculate recommended capacity
    if best_avg_response < 200:
        capacity_multiplier = 1.5
        recommendation = "Excellent performance - can handle 50% more load"
    elif best_avg_response < 500:
        capacity_multiplier = 1.2
        recommendation = "Good performance - can handle 20% more load"
    elif best_avg_response < 1000:
        capacity_multiplier = 1.0
        recommendation = "Adequate performance - at recommended capacity"
    else:
        capacity_multiplier = 0.7
        recommendation = "Poor performance - consider scaling up"
    
    return {
        "recommended_max_users": int(best_vus * capacity_multiplier),
        "current_max_tested": best_vus,
        "recommendation": recommendation,
        "avg_response_time_at_capacity": best_avg_response
    }


@router.post("/test/quick")
async def quick_performance_test(target_url: HttpUrl) -> PerformanceTestResponse:
    """
    Run a quick smoke test with default settings.
    
    Useful for quick health checks and basic performance validation.
    
    **Settings:**
    - Test Type: Smoke
    - 5 virtual users
    - 2 minute duration
    - Tests /health endpoint
    
    **Example:**
    ```
    POST /api/performance/test/quick
    {
        "target_url": "https://api.example.com"
    }
    ```
    """
    request = PerformanceTestRequest(
        target_url=target_url,
        test_type="smoke",
        vus=5,
        duration="2m",
        endpoints=[{"method": "GET", "path": "/health"}]
    )
    
    return await start_performance_test(request)


@router.post("/test/load")
async def run_load_test(
    target_url: HttpUrl,
    vus: int = 50,
    duration: str = "5m",
    ramp_up: str = "1m"
) -> PerformanceTestResponse:
    """
    Run a standard load test.
    
    Tests system behavior under expected normal and peak load.
    Gradually ramps up to target VUs, maintains steady load, then ramps down.
    
    **Use Cases:**
    - Validate performance under normal conditions
    - Establish baseline metrics
    - Pre-deployment validation
    
    **Parameters:**
    - vus: Number of concurrent users (default: 50)
    - duration: How long to maintain peak load (default: 5m)
    - ramp_up: Time to reach peak load (default: 1m)
    """
    request = PerformanceTestRequest(
        target_url=target_url,
        test_type="load",
        vus=vus,
        duration=duration,
        ramp_up=ramp_up
    )
    
    return await start_performance_test(request)


@router.post("/test/stress")
async def run_stress_test(
    target_url: HttpUrl,
    vus: int = 100
) -> PerformanceTestResponse:
    """
    Run a stress test to find system breaking point.
    
    Progressively increases load beyond normal capacity:
    - 1x normal load (baseline)
    - 1.5x normal load
    - 2x normal load
    - 2.5x normal load
    - 3x normal load (breaking point)
    
    **Use Cases:**
    - Find maximum capacity
    - Identify bottlenecks
    - Test failure modes
    - Capacity planning
    
    **Duration:** ~16 minutes (progressive stages)
    
    **Warning:** May cause service degradation or failure at peak load.
    Only run on non-production or isolated environments.
    """
    request = PerformanceTestRequest(
        target_url=target_url,
        test_type="stress",
        vus=vus
    )
    
    return await start_performance_test(request)


@router.post("/test/spike")
async def run_spike_test(
    target_url: HttpUrl,
    vus: int = 50
) -> PerformanceTestResponse:
    """
    Run a spike test to simulate sudden traffic surge.
    
    Simulates scenarios like:
    - Breaking news / viral content
    - Flash sales (Black Friday)
    - Marketing campaign launches
    - DDoS-like traffic patterns
    
    **Test Pattern:**
    1. Normal load (50 VUs)
    2. Sudden 5x spike (250 VUs)
    3. Maintain spike for 1 minute
    4. Return to normal
    5. Recovery observation
    
    **Duration:** ~4 minutes
    
    **What to watch:**
    - How quickly system responds to spike
    - Error rates during spike
    - Recovery time after spike
    """
    request = PerformanceTestRequest(
        target_url=target_url,
        test_type="spike",
        vus=vus
    )
    
    return await start_performance_test(request)


@router.post("/test/capacity")
async def run_capacity_test(
    target_url: HttpUrl,
    base_vus: int = 50,
    max_vus: int = 500
) -> PerformanceTestResponse:
    """
    Run a capacity test to find optimal sustainable load.
    
    Gradually increases load in incremental steps to identify:
    - Maximum sustainable concurrent users
    - Optimal operating capacity
    - Performance degradation thresholds
    
    **Test Pattern:**
    - Starts at base_vus
    - Increases in 20% steps
    - Each step runs for 3 minutes
    - Sustains max load for 5 minutes
    
    **Use Cases:**
    - Infrastructure sizing
    - Cost optimization
    - SLA definition
    - Scaling policy configuration
    
    **Duration:** Varies based on max_vus (typically 20-40 minutes)
    
    **Example:**
    ```json
    {
        "target_url": "https://api.example.com",
        "base_vus": 50,
        "max_vus": 500
    }
    ```
    Result: Tests 50, 100, 150, 200, 250, 300, 350, 400, 450, 500 VUs
    """
    request = PerformanceTestRequest(
        target_url=target_url,
        test_type="capacity",
        vus=base_vus,
        max_vus=max_vus
    )
    
    return await start_performance_test(request)


@router.post("/test/soak")
async def run_soak_test(
    target_url: HttpUrl,
    vus: int = 100,
    duration: str = "30m"
) -> PerformanceTestResponse:
    """
    Run a soak (endurance) test for extended duration.
    
    Maintains moderate load (70% capacity) for extended period to detect:
    - Memory leaks
    - Resource exhaustion
    - Performance degradation over time
    - Database connection pool issues
    - Cache invalidation problems
    
    **Test Pattern:**
    - Ramp up to 70% capacity (5 min)
    - Maintain steady load (30 min default)
    - Ramp down (5 min)
    
    **Use Cases:**
    - Pre-production stability validation
    - Long-running service verification
    - Continuous operation testing
    
    **Duration Options:**
    - Quick: 15m (minimal soak)
    - Standard: 30m (recommended)
    - Extended: 1h-2h (thorough)
    - Marathon: 4h-24h (comprehensive)
    
    **Warning:** Long-running tests consume resources.
    Monitor system metrics throughout the test.
    
    **Example:**
    ```json
    {
        "target_url": "https://api.example.com",
        "vus": 100,
        "duration": "1h"
    }
    ```
    """
    request = PerformanceTestRequest(
        target_url=target_url,
        test_type="soak",
        vus=vus,
        soak_duration=duration
    )
    
    return await start_performance_test(request)


@router.get("/db/{repo_id}")
async def get_performance_runs(repo_id: str):
    from backend.app.integrations.supabase_service import _get_conn

    conn = _get_conn()

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                run_id,
                test_type,
                duration,
                vus_max,
                total_requests,
                success_rate,
                avg_response_time,
                p95_response_time,
                created_at
            FROM performance_runs
            WHERE repo_id = %s
            ORDER BY created_at DESC
            LIMIT 50
            """,
            (repo_id,)
        )

        rows = cur.fetchall()

    results = []

    for r in rows:
        results.append({
            "run_id": r[0],
            "test_type": r[1],
            "duration": r[2],
            "vus": r[3],
            "requests": r[4],
            "success_rate": r[5],
            "avg_response_time": r[6],
            "p95_response_time": r[7],
            "created_at": r[8]
        })

    return {"results": results}


@router.get("/db/run/{run_id}")
async def get_performance_run(run_id: str):
    from backend.app.integrations.supabase_service import fetch_performance_run

    result = fetch_performance_run(run_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Performance run not found"
        )

    return result