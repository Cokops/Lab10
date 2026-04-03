import grpc
import json
import time

# Import generated gRPC code
# Note: This requires generating the Python stubs from the .proto file
# python -m grpc_tools.protoc -I../proto --python_out=. --grpc_python_out=. ../proto/data.proto

class DataServiceClient:
    def __init__(self, host="localhost", port=50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        # The following line will be available after generating the stubs
        # self.stub = data_pb2_grpc.DataServiceStub(self.channel)
    
    def get_complex_data(self, timestamp: str):
        # This is a placeholder for the actual gRPC call
        # request = data_pb2.DataRequest(timestamp=timestamp)
        # response = self.stub.GetComplexData(request)
        # return response
        
        # Simulate response for now
        return {
            "id": 1,
            "name": "PythonClientSimulated",
            "details": {
                "source": "python-grpc-client",
                "timestamp": timestamp,
                "version": "1.0",
                "simulated": True
            }
        }
    
    def close(self):
        self.channel.close()

if __name__ == "__main__":
    client = DataServiceClient()
    try:
        response = client.get_complex_data(time.strftime("%Y-%m-%d %H:%M:%S"))
        print("Received data:", json.dumps(response, indent=2))
    finally:
        client.close()