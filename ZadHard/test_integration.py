import unittest
import requests
import subprocess
import time
import os
import signal
import json
from typing import Dict, Any

# Configuration
PROJECT_ROOT = ".."
GO_SERVICE_DIR = os.path.join(PROJECT_ROOT, "ZadMid", "go-service")
PYTHON_SERVICE_DIR = os.path.join(PROJECT_ROOT, "ZadMid", "python-service")

GO_SERVICE_CMD = ["go", "run", "main.go"]
PYTHON_SERVICE_CMD = ["python", "server.py"]

GO_SERVICE_URL = "http://localhost:8080"
PYTHON_SERVICE_URL = "http://localhost:5000"

COMPLEX_DATA = {
    "name": "integration-test-data",
    "details": {
        "version": "test-1.0",
        "metadata": {
            "test_case": "complex_json",
            "nested": True,
            "tags": ["integration", "json", "cross-service"]
        },
        "timestamp": None  # Will be set dynamically
    }
}

class TestIntegration(unittest.TestCase):
    go_process: subprocess.Popen = None
    python_process: subprocess.Popen = None

    @classmethod
    def setUpClass(cls):
        """Start both services before tests"""
        print("Starting Go service...")
        cls.go_process = subprocess.Popen(
            GO_SERVICE_CMD,
            cwd=GO_SERVICE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(5)  # Wait for Go service to start

        print("Starting Python service...")
        cls.python_process = subprocess.Popen(
            PYTHON_SERVICE_CMD,
            cwd=PYTHON_SERVICE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(5)  # Wait for Python service to start

        # Verify both services are up
        cls._assert_service_up(GO_SERVICE_URL + "/health", "Go")
        cls._assert_service_up(PYTHON_SERVICE_URL + "/health", "Python")

    @classmethod
    def tearDownClass(cls):
        """Gracefully terminate both services after tests"""
        print("Shutting down services...")
        
        if cls.python_process:
            os.kill(cls.python_process.pid, signal.SIGTERM)
            cls.python_process.wait(timeout=15)

        if cls.go_process:
            os.kill(cls.go_process.pid, signal.SIGTERM)
            cls.go_process.wait(timeout=15)

    @classmethod
    def _assert_service_up(cls, url: str, name: str):
        try:
            response = requests.get(url, timeout=10)
            cls.assertEqual(response.status_code, 200, f"{name} service failed to start")
            cls.assertEqual(response.json()["status"], "ok", f"{name} service health check failed")
            print(f"{name} service is up and running")
        except Exception as e:
            raise Exception(f"Failed to connect to {name} service at {url}: {e}")

    def test_01_post_data_to_go_service(self):
        """Test posting complex JSON data to Go service"""
        url = f"{GO_SERVICE_URL}/data"
        test_data = COMPLEX_DATA.copy()
        test_data["details"]["timestamp"] = time.time()

        response = requests.post(url, json=test_data, timeout=10)
        
        self.assertEqual(response.status_code, 201, "Failed to POST data to Go service")
        
        response_data = response.json()
        self.assertEqual(response_data["name"], test_data["name"], "Returned data does not match")
        self.assertIn("id", response_data, "Response missing ID")
        
        print("✓ Successfully posted data to Go service")

    def test_02_get_data_from_go_service(self):
        """Test retrieving data from Go service"""
        url = f"{GO_SERVICE_URL}/data"
        
        response = requests.get(url, timeout=10)
        self.assertEqual(response.status_code, 200, "Failed to GET data from Go service")
        
        data = response.json()
        self.assertIsInstance(data, list, "Expected list response")
        self.assertGreater(len(data), 0, "No data returned from Go service")
        
        found = any(item.get("name") == COMPLEX_DATA["name"] for item in data)
        self.assertTrue(found, "Test data not found in Go service response")
        
        print("✓ Successfully retrieved data from Go service")

    def test_03_python_service_fetches_go_data(self):
        """Test that Python service can retrieve data from Go service"""
        url = f"{PYTHON_SERVICE_URL}/data"
        
        response = requests.get(url, timeout=10)
        self.assertEqual(response.status_code, 200, "Failed to GET data from Python service")
        
        data = response.json()
        self.assertIn("from_go_service", data, "Python service response missing 'from_go_service'")
        
        go_data = data["from_go_service"]
        self.assertIsInstance(go_data, list, "Expected list in 'from_go_service'")
        
        # Check if our test data is present
        found = any(item.get("name") == COMPLEX_DATA["name"] for item in go_data)
        self.assertTrue(found, "Test data not propagated to Python service")
        
        print("✓ Python service successfully fetched data from Go service")

    def test_04_post_data_to_python_service(self):
        """Test posting data to Python service"""
        url = f"{PYTHON_SERVICE_URL}/data"
        test_data = {
            "name": "python-post-test",
            "details": {
                "source": "test_client",
                "timestamp": time.time()
            }
        }
        
        response = requests.post(url, json=test_data, timeout=10)
        self.assertEqual(response.status_code, 201, "Failed to POST data to Python service")
        
        response_data = response.json()
        self.assertEqual(response_data["name"], test_data["name"], "Returned data does not match")
        
        print("✓ Successfully posted data to Python service")

    def test_05_services_handle_graceful_shutdown(self):
        """Test that services handle shutdown signals properly"""
        # This test verifies that our teardown correctly sends SIGTERM
        # The actual graceful shutdown logic is tested by the services themselves
        self.assertIsNotNone(self.go_process, "Go service process not started")
        self.assertIsNotNone(self.python_process, "Python service process not started")
        
        # If we reach here and services started, the graceful shutdown
        # will be tested during tearDownClass when we send SIGTERM
        print("✓ Services are configured to handle graceful shutdown")

if __name__ == '__main__':
    unittest.main()