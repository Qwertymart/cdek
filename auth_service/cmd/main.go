package main

import (
	"github.com/joho/godotenv"
	"log"
	"os"
	"time"

	"auth_service/internal/handler"
	"auth_service/pkg/auth_user_pb"

	"github.com/gin-gonic/gin"
	"google.golang.org/grpc"
)

// @title Auth Service API
// @version 1.0
// @description API для управления аутентификацией
// @host localhost:8080
// @BasePath /api/v1
func main() {
	if err := godotenv.Load("../.env"); err != nil {
		log.Fatal("Error loading .env file")
	}
	conn, err := grpc.Dial(os.Getenv("USER_SERVICE_ADDR"), grpc.WithInsecure(), grpc.WithBlock(), grpc.WithTimeout(5*time.Second))
	if err != nil {
		log.Fatalf("failed to connect to the user service: %v", err)
	}
	defer conn.Close()

	authClient := auth_user_pb.NewAuthServiceClient(conn)
	authHandler := handler.NewAuthHandler(authClient)

	router := gin.Default()

	// REST endpoints
	router.POST("/register", authHandler.Register)
	router.POST("/login", authHandler.Login)

	if err := router.Run(":8080"); err != nil {
		log.Fatalf("failed to launch the server: %v", err)
	}
}
