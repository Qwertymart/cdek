package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"dashboard_service/internal/handler"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {
	// Загружаем переменные окружения из .env файла
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: .env file not found: %v", err)
	}

	// Получаем адрес gRPC сервера из переменных окружения или используем значение по умолчанию
	grpcAddress := os.Getenv("GRPC_ADDRESS")
	if grpcAddress == "" {
		grpcAddress = "localhost:50051" // значение по умолчанию
	}

	// Получаем порт HTTP сервера из переменных окружения или используем значение по умолчанию
	httpPort := os.Getenv("HTTP_PORT")
	if httpPort == "" {
		httpPort = "8080"
	}

	// Получаем режим Gin из переменных окружения
	ginMode := os.Getenv("GIN_MODE")
	if ginMode == "" {
		ginMode = gin.ReleaseMode
	}
	gin.SetMode(ginMode)

	log.Printf("Starting dashboard service...")
	log.Printf("gRPC address: %s", grpcAddress)
	log.Printf("HTTP port: %s", httpPort)

	// Создаем обработчик аналитики
	analysisHandler, err := handlers.NewAnalysisHandler(grpcAddress)
	if err != nil {
		log.Fatalf("Failed to create analysis handler: %v", err)
	}
	defer func() {
		if err := analysisHandler.Close(); err != nil {
			log.Printf("Error closing analysis handler: %v", err)
		}
	}()

	// Настраиваем Gin router
	router := gin.New()

	// Добавляем middleware для логирования и восстановления после паники
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// Добавляем CORS middleware
	router.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	// Регистрируем маршруты
	api := router.Group("/api/v1")
	{
		api.POST("/analysis", analysisHandler.GetAnalysisData)
		api.GET("/health", analysisHandler.HealthCheck)
	}

	// Добавляем базовый маршрут для проверки работы сервера
	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Dashboard Service is running",
			"version": "1.0.0",
			"status":  "ok",
		})
	})

	// Настраиваем HTTP сервер
	srv := &http.Server{
		Addr:         ":" + httpPort,
		Handler:      router,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Запускаем сервер в отдельной горутине
	go func() {
		log.Printf("Starting HTTP server on port %s", httpPort)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	// Ждем сигнал для graceful shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server...")

	// Graceful shutdown с таймаутом
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Printf("Server forced to shutdown: %v", err)
	}

	log.Println("Server exited")
}
