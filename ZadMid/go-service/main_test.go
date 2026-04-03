package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
)

func TestHealthHandler(t *testing.T) {
	r := gin.Default()
	r.GET("/health", healthHandler)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/health", nil)
	r.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var response map[string]string
	if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
		t.Fatalf("Failed to unmarshal JSON: %v", err)
	}

	if response["status"] != "ok" {
		t.Errorf("Expected status 'ok', got '%s'", response["status"])
	}
}

func TestDataHandler_Get(t *testing.T) {
	r := gin.Default()
	r.GET("/data", getDataHandler)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/data", nil)
	r.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var response []Data
	if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
		t.Fatalf("Failed to unmarshal JSON: %v", err)
	}

	if len(response) == 0 {
		t.Errorf("Expected data, got empty array")
	}
}

func TestDataHandler_Post(t *testing.T) {
	// Test POST /data
	newData := Data{
		ID:   2,
		Name: "test-data-post",
		Details: map[string]interface{}{
			"test":    "true",
			"created": time.Now().Format(time.RFC3339),
		},
	}
	jsonData, _ := json.Marshal(newData)

	r := gin.Default()
	r.POST("/data", postDataHandler)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/data", bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	if w.Code != http.StatusCreated {
		t.Errorf("Expected status %d, got %d", http.StatusCreated, w.Code)
	}

	var response Data
	if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
		t.Fatalf("Failed to unmarshal JSON: %v", err)
	}

	if response.Name != "test-data-post" {
		t.Errorf("Expected name 'test-data-post', got '%s'", response.Name)
	}
}