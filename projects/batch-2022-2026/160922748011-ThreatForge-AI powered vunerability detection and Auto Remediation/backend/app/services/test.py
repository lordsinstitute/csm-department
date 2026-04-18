from performance_service import run_k6_test, generate_test_id

config = {
    "test_type": "load",
    "vus": 10,
    "duration": "30s",
    "endpoints": [{"method": "GET", "path": "/"}]
}

test_id = generate_test_id("load")
result = run_k6_test(test_id, "https://lords.ac.in/", config)
print(result)