FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY proto/ ./proto/

# Если есть сгенерированные gRPC stubs
# COPY *_pb2.py *_pb2_grpc.py ./

CMD ["python", "client.py"]