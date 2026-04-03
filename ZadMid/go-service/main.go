package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
)

// Data represents a complex data structure to be passed between services
type Data struct {
	ID      int                    `json:"id"`
	Name    string                 `json:"name"`
	Details map[string]interface{} `json:"details"`
}

var dataStore = []Data{
	{
		ID:   1,
		Name: "example-data",
		Details: map[string]interface{}{
			"version":    "1.0",
			"created_at": time.Now().Format(time.RFC3339),
			"metadata": map[string]string{
				"source": "go-service",
				"env":    "development",
			},
		},
	},
}

func main() {
	// Initialize Gin router
	r := gin.Default()

	// Define API endpoints
	r.GET("/health", healthHandler)
	r.GET("/data", getDataHandler)
	r.POST("/data", postDataHandler)

	// Run server in a separate goroutine
	server := &http.Server{
		Addr:    ":8080",
		Handler: r,
	}

	go func() {
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			panic(err)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c

	// Graceful shutdown
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := server.Shutdown(shutdownCtx); err != nil {
		panic(err)
	}

	println("\nGo service stopped gracefully")
}

func healthHandler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}

func getDataHandler(c *gin.Context) {
	c.JSON(http.StatusOK, dataStore)
}

func postDataHandler(c *gin.Context) {
	var newData Data
	if err := c.BindJSON(&newData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	dataStore = append(dataStore, newData)
	c.JSON(http.StatusCreated, newData)
}