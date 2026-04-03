import unittest
import requests
import threading
import time
import subprocess
import os
import signal

# Configuration
PYTHON_SERVER_CMD = ["python", "server.py"]
SERVER_URL = "http://localhost:5000"
GO_SERVICE_CMD = ["go", "run", "main.go"]
GO_SERVICE_URL = "http://localhost:8080"

class TestPythonService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start Go service first
        cls.go_process = subprocess.Popen(
            GO_SERVICE_CMD,
            cwd="../go-service",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)  # Give Go service time to start

        # Start Python service
        cls.python_process = subprocess.Popen(
            PYTHON_SERVER_CMD,
            cwd=".",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)  # Give Python service time to start

    @classmethod
    def tearDownClass(cls):
        # Gracefully terminate processes
        if cls.python_process:
            os.kill(cls.python_process.pid, signal.SIGTERM)
            cls.python_process.wait(timeout=10)

        if cls.go_process:
            os.kill(cls.go_process.pid, signal.SIGTERM)
            cls.go_process.wait(timeout=10)

    def test_health_endpoint(self):
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_get_data_endpoint(self):
        response = requests.get(f"{SERVER_URL}/data", timeout=5)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("local", data)
        self.assertIn("from_go_service", data)
        self.assertIsInstance(data["local"], list)
        self.assertIsInstance(data["from_go_service"], list)

    def test_post_data_endpoint(self):
        test_data = {
            "name": "test-data-from-python-test",
            "details": {
                "test": "true",
                "source": "test"
            }
        }
        
        response = requests.post(
            f"{SERVER_URL}/data",
            json=test_data,
            timeout=5
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data["name"], test_data["name"])
        self.assertIn("id", response_data)


if __name__ == '__main__':
    unittest.main()