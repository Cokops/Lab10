FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .

# Copy generated gRPC stubs if they exist
# COPY data_pb2.py data_pb2_grpc.py ./

EXPOSE 50051

CMD ["python", "client.py"]