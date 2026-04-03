from flask import Flask, jsonify, request
import signal
import sys
import time
import requests

app = Flask(__name__)

# Simulate data store
DATA_STORE = [
    {
        "id": 1,
        "name": "python-data",
        "details": {
            "version": "1.0",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "metadata": {
                "source": "python-service",
                "env": "development"
            }
        }
    }
]

go_service_url = "http://localhost:8080/data"

@app.route('/health', methods=['GET'])
def health():
    return jsonify(status="ok"), 200

@app.route('/data', methods=['GET'])
def get_data():
    # Also fetch data from Go service
    try:
        resp = requests.get(go_service_url, timeout=5)
        go_data = resp.json() if resp.status_code == 200 else []
    except requests.RequestException:
        go_data = []
    
    return jsonify(local=DATA_STORE, from_go_service=go_data)

@app.route('/data', methods=['POST'])
def post_data():
    if not request.is_json:
        return jsonify(error="Content-Type must be application/json"), 400
    
    data = request.json
    data['id'] = len(DATA_STORE) + 1
    DATA_STORE.append(data)
    
    return jsonify(data), 201

# Graceful shutdown
def signal_handler(sig, frame):
    print('\nShutting down Python service gracefully...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    print("Python service starting on :5000")
    app.run(host='0.0.0.0', port=5000)