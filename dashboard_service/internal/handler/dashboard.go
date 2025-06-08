package handlers

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	"dashboard_service/pkg/dashboard_anal_pb"
)

// AnalysisHandler структура для обработки запросов аналитики
type AnalysisHandler struct {
	grpcClient dashboard_anal_pb.AnalysisServiceClient
	grpcConn   *grpc.ClientConn
}

// NewAnalysisHandler создает новый экземпляр хэндлера
func NewAnalysisHandler(grpcAddress string) (*AnalysisHandler, error) {
	conn, err := grpc.Dial(grpcAddress, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, fmt.Errorf("failed to connect to gRPC server: %v", err)
	}

	client := dashboard_anal_pb.NewAnalysisServiceClient(conn)

	return &AnalysisHandler{
		grpcClient: client,
		grpcConn:   conn,
	}, nil
}

func extractSourceNames(sources []Sources) []string {
	names := make([]string, 0, len(sources))
	for _, src := range sources {
		names = append(names, src.Name)
	}
	return names
}

// Close закрывает соединение с gRPC
func (h *AnalysisHandler) Close() error {
	if h.grpcConn != nil {
		return h.grpcConn.Close()
	}
	return nil
}

// FilterRequest структура для входящих HTTP запросов
type FilterRequest struct {
	Salary     []uint32 `json:"salaryRange,omitempty"`
	Position   string   `json:"positions,omitempty"`
	Experience []uint32 `json:"experience,omitempty"`
	Regions    []string `json:"regions,omitempty"`
	Companies  []string `json:"companies,omitempty"`
	Sources    []string `json:"sources,omitempty"`
}

type Sources struct {
	ID   uint32 `json:"id"`
	Name string `json:"name"`
	URL  string `json:"url"`
	Av   bool   `json:"av"`
}

type FilterRequest2 struct {
	Salary     []uint32  `json:"salaryRange,omitempty"`
	Position   string    `json:"positions,omitempty"`
	Experience []uint32  `json:"experience,omitempty"`
	Regions    []string  `json:"regions,omitempty"`
	Companies  []string  `json:"companies,omitempty"`
	Sources    []Sources `json:"sources,omitempty"`
}

// AnalysisHTTPResponse структура для HTTP ответа
type AnalysisHTTPResponse struct {
	Success bool                  `json:"success"`
	Error   string                `json:"error,omitempty"`
	PDF     string                `json:"pdf_data,omitempty"` // base64 encoded PDF
	Images  []ImageResponse       `json:"images,omitempty"`
	Items   *AnalysisItemResponse `json:"items,omitempty"`
	Tables  []TableResponse       `json:"tables,omitempty"`
}

type ImageResponse struct {
	Name string `json:"name"`
	Type uint32 `json:"type"`
	Data string `json:"data"` // base64 encoded
	Size int64  `json:"size"`
}

type AnalysisItemResponse struct {
	TotalNumber uint32  `json:"total_number"`
	Average     float32 `json:"average"`
	Median      uint32  `json:"median"`
}

type TableResponse struct {
	Name       string `json:"name"`
	Salary     uint32 `json:"salary"`
	Link       string `json:"link"`
	Experience uint32 `json:"experience"`
	Region     string `json:"region"`
}

// GetAnalysisData основной хэндлер для получения данных аналитики (Gin версия)
func (h *AnalysisHandler) GetAnalysisData(c *gin.Context) {
	// Парсим входящий JSON
	var filterReq FilterRequest2
	if err := c.ShouldBindJSON(&filterReq); err != nil {
		log.Printf("Error decoding request: %v", err)
		c.JSON(http.StatusBadRequest, AnalysisHTTPResponse{
			Success: false,
			Error:   "Invalid JSON format",
		})
		return
	}

	jsonData, _ := json.Marshal(filterReq)
	log.Printf("Полученные фильтры: %s", string(jsonData))
	log.Println(filterReq)
	log.Printf("Received analysis request: %+v", filterReq)

	// Преобразуем в protobuf запрос
	grpcReq := &dashboard_anal_pb.AnalysisRequest{
		Salary:     filterReq.Salary,
		Position:   filterReq.Position,
		Experience: filterReq.Experience,
		Regions:    filterReq.Regions,
		Companies:  filterReq.Companies,
		Sources:    extractSourceNames(filterReq.Sources),
	}

	// Создаем контекст с таймаутом
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Вызываем gRPC сервис
	grpcResp, err := h.grpcClient.GetAnalysisData(ctx, grpcReq)
	if err != nil {
		log.Printf("Error calling gRPC service: %v", err)
		c.JSON(http.StatusInternalServerError, AnalysisHTTPResponse{
			Success: false,
			Error:   "Failed to get analysis data",
		})
		return
	}

	// Проверяем успешность ответа от gRPC
	if !grpcResp.Success {
		log.Printf("gRPC service returned error: %s", grpcResp.Error)
		c.JSON(http.StatusOK, AnalysisHTTPResponse{
			Success: false,
			Error:   grpcResp.Error,
		})
		return
	}

	httpResp := h.buildHTTPResponse(grpcResp)

	// Отправляем ответ
	c.JSON(http.StatusOK, httpResp)
	log.Printf("Successfully processed analysis request")
}

/*
	func (h *AnalysisHandler) GetAnalysisData(c *gin.Context) {
		var filterReq FilterRequest
		if err := c.ShouldBindJSON(&filterReq); err != nil {
			log.Printf("Error decoding request: %v", err)
			c.JSON(http.StatusBadRequest, AnalysisHTTPResponse{
				Success: false,
				Error:   "Invalid JSON format",
			})
			return
		}

		log.Printf("Received mock analysis request: %+v", filterReq)

		// МОК ДАННЫЕ (вместо gRPC вызова)
		mockResponse := AnalysisHTTPResponse{
			Success: true,
			PDF:     "JVBERi0xLjQK...", // base64-заглушка
			Images: []ImageResponse{
				{
					Name: "Salary Chart",
					Type: 1,
					Data: "iVBORw0KGgoAAAANSUhEUgAA...", // base64-заглушка
					Size: 12345,
				},
			},
			Items: &AnalysisItemResponse{
				TotalNumber: 512,
				Average:     125000.75,
				Median:      120000,
			},
			Tables: []TableResponse{
				{
					Name:       "Backend Developer",
					Salary:     130000,
					Link:       "https://example.com/vacancy/123",
					Experience: 3,
					Region:     "Москва",
				},
				{
					Name:       "Frontend Developer",
					Salary:     110000,
					Link:       "https://example.com/vacancy/456",
					Experience: 2,
					Region:     "Санкт-Петербург",
				},
			},
		}

		// Возврат мок-данных
		c.JSON(http.StatusOK, mockResponse)
		log.Printf("Returned mock response for analysis")
	}
*/
func (h *AnalysisHandler) buildHTTPResponse(grpcResp *dashboard_anal_pb.AnalysisResponse) AnalysisHTTPResponse {
	resp := AnalysisHTTPResponse{
		Success: grpcResp.Success,
		Error:   grpcResp.Error,
	}

	if len(grpcResp.PdfData) > 0 {
		resp.PDF = base64.StdEncoding.EncodeToString(grpcResp.PdfData)
	}

	if len(grpcResp.Images) > 0 {
		resp.Images = make([]ImageResponse, len(grpcResp.Images))
		for i, img := range grpcResp.Images {
			resp.Images[i] = ImageResponse{
				Name: img.Name,
				Type: img.Type,
				Data: base64.StdEncoding.EncodeToString(img.ImageData),
				Size: img.Size,
			}
		}
	}

	if grpcResp.Items != nil {
		resp.Items = &AnalysisItemResponse{
			TotalNumber: grpcResp.Items.TotalNumber,
			Average:     grpcResp.Items.Avg,
			Median:      grpcResp.Items.Median,
		}
	}

	if len(grpcResp.Table) > 0 {
		resp.Tables = make([]TableResponse, len(grpcResp.Table))
		for i, table := range grpcResp.Table {
			resp.Tables[i] = TableResponse{
				Name:       table.Name,
				Salary:     table.Salary,
				Link:       table.Link,
				Experience: table.Experience,
				Region:     table.Region,
			}
		}
	}

	return resp
}

// HealthCheck хэндлер для проверки состояния сервиса
func (h *AnalysisHandler) HealthCheck(c *gin.Context) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// Проверяем доступность gRPC сервиса пустым запросом
	_, err := h.grpcClient.GetAnalysisData(ctx, &dashboard_anal_pb.AnalysisRequest{})

	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"status": "unhealthy",
			"error":  err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "healthy",
	})
}
