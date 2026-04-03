# Integration Tests

This directory contains integration and end-to-end tests for the cross-service functionality.

## Test Suites

- `test_integration.py`: Full integration test covering both services
- `test_go_service.py`: Dedicated test suite for Go service
- `test_server.py`: Integration tests for Python service

## Go Service Tests

`test_go_service.py` verifies:
- Service startup and health check
- JSON structure and data types
- POST/GET data persistence
- Error handling for invalid requests
- Graceful shutdown behavior

## Requirements

- Go 1.22+
- Python 3.9+
- Flask, requests (Python)
- Gin (Go)

## Usage

```bash
# Run all integration tests
python test_integration.py

# Run Go service specific tests
python test_go_service.py

# Run Python service tests
python test_server.py
```

## docker-compose.yml

Basic service orchestration for testing:
```yaml
version: '3'

services:
  go-service:
    build: ../ZadMid/go-service
    ports:
      - "8080:8080"
    working_dir: /app
    command: go run main.go

  python-service:
    build: ../ZadMid/python-service
    ports:
      - "5000:5000"
    working_dir: /app
    command: python server.py
    depends_on:
      - go-service
```

> Note: Dockerfiles need to be created in respective service directories.