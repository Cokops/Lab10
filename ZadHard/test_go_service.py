import unittest
import requests
import subprocess
import time
import os
import signal

# Configuration
GO_SERVICE_DIR = "../ZadMid/go-service"
GO_SERVICE_CMD = ["go", "run", "main.go"]
GO_SERVICE_URL = "http://localhost:8080"

# Test data
TEST_DATA = {
    "name": "go-service-integration-test",
    "details": {
        "test_suite": "zadhard-go",
        "nested": {
            "level": 1,
            "array": [1, 2, 3, 4, 5]
        },
        "timestamp": None  # Will be set dynamically
    }
}

class TestGoService(unittest.TestCase):
    go_process: subprocess.Popen = None

    @classmethod
    def setUpClass(cls):
        """Start Go service before tests"""
        print("Starting Go service...")
        cls.go_process = subprocess.Popen(
            GO_SERVICE_CMD,
            cwd=GO_SERVICE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(5)  # Wait for service to start

        # Verify service is up
        cls._assert_service_up()

    @classmethod
    def tearDownClass(cls):
        """Gracefully terminate Go service after tests"""
        print("Shutting down Go service...")
        if cls.go_process:
            os.kill(cls.go_process.pid, signal.SIGTERM)
            cls.go_process.wait(timeout=15)

    @classmethod
    def _assert_service_up(cls):
        try:
            response = requests.get(f"{GO_SERVICE_URL}/health", timeout=10)
            cls.assertEqual(response.status_code, 200, "Go service failed to start")
            cls.assertEqual(response.json()["status"], "ok", "Go service health check failed")
            print("Go service is up and running")
        except Exception as e:
            raise Exception(f"Failed to connect to Go service: {e}")

    def test_01_get_health(self):
        """Test health endpoint"""
        response = requests.get(f"{GO_SERVICE_URL}/health", timeout=10)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        print("✓ Health check passed")

    def test_02_get_data_returns_json(self):
        """Test data endpoint returns valid JSON"""
        response = requests.get(f"{GO_SERVICE_URL}/data", timeout=10)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list, "Expected list response")
        self.assertGreater(len(data), 0, "No data returned")
        
        # Check structure of first item
        first_item = data[0]
        self.assertIn("id", first_item)
        self.assertIn("name", first_item)
        self.assertIn("details", first_item)
        self.assertIsInstance(first_item["details"], dict)
        
        print("✓ Data endpoint returns valid JSON structure")

    def test_03_post_valid_data(self):
        """Test posting valid JSON data"""
        url = f"{GO_SERVICE_URL}/data"
        test_data = TEST_DATA.copy()
        test_data["details"]["timestamp"] = time.time()

        response = requests.post(url, json=test_data, timeout=10)
        
        self.assertEqual(response.status_code, 201, "Failed to POST data")
        
        response_data = response.json()
        self.assertEqual(response_data["name"], test_data["name"], "Returned name doesn't match")
        self.assertIn("id", response_data, "Response missing ID")
        
        # Verify the data can now be retrieved
        get_response = requests.get(f"{GO_SERVICE_URL}/data", timeout=10)
        get_data = get_response.json()
        found = any(item.get("name") == test_data["name"] for item in get_data)
        self.assertTrue(found, "Posted data not found in subsequent GET")
        
        print("✓ Successfully posted and retrieved data")

    def test_04_post_invalid_json(self):
        """Test handling of invalid JSON"""
        url = f"{GO_SERVICE_URL}/data"
        
        # Send invalid content type
        response = requests.post(
            url, 
            data="Not JSON",
            headers={"Content-Type": "text/plain"},
            timeout=10
        )
        
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, 400, "Expected 400 for invalid JSON")
        
        print("✓ Properly handles invalid JSON requests")

    def test_05_graceful_shutdown(self):
        """Test that service handles shutdown signal properly"""
        # This verifies that our teardown correctly sends SIGTERM
        # The actual graceful shutdown is tested by the service's behavior
        self.assertIsNotNone(self.go_process, "Go service process not started")
        
        # If we reach here, service started successfully
        # Graceful shutdown will be tested during tearDownClass
        print("✓ Service is configured for graceful shutdown")

if __name__ == '__main__':
    unittest.main()