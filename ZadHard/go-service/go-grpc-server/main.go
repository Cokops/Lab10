package main

import (
	"context"
	"log"
	"net"

	pb "go-grpc-server/proto"
	"google.golang.org/grpc"
)

// server is the struct that implements the gRPC service
type server struct {
	pb.UnimplementedDataServiceServer
}

// DataRequest represents a request for data
type DataRequest struct {
	Timestamp string `json:"timestamp"`
}

// DataResponse represents a complex response structure
type DataResponse struct {
	Id      int                    `json:"id"`
	Name    string                 `json:"name"`
	Details map[string]interface{} `json:"details"`
}

// GetComplexData returns a complex JSON-like structure
func (s *server) GetComplexData(ctx context.Context, req *pb.DataRequest) (*pb.DataResponse, error) {
	return &pb.DataResponse{
		Id:   1,
		Name: "GoServiceData",
		Details: map[string]string{
			"source":    "go-grpc-server",
			"timestamp": req.Timestamp,
			"version":   "1.0",
		},
	}, nil
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterDataServiceServer(grpcServer, &server{})

	log.Println("gRPC server listening on :50051")
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}
