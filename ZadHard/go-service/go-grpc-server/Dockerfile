FROM golang:1.22-alpine

WORKDIR /app

COPY go.mod .
RUN go mod download

COPY *.go .

# Install protoc and gRPC plugins (if using .proto files)
# RUN apk add --no-cache protobuf grpc-dev

RUN go build -o main .

EXPOSE 50051

CMD ["./main"]