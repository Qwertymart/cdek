package handler

import (
	"auth_service/pkg/auth_user_pb"
	"github.com/dgrijalva/jwt-go"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"log"
	"net/http"
	"os"
	"time"
)

var jwtSecret []byte

func init() {
	if err := godotenv.Load("../.env"); err != nil {
		log.Fatal("Error loading .env file")
	}

	secret := os.Getenv("JWT_SECRET")
	if secret == "" {
		log.Fatal("JWT_SECRET environment variable is not set")
	}
	jwtSecret = []byte(secret)
}

type AuthHandler struct {
	authClient auth_user_pb.AuthServiceClient
}

func NewAuthHandler(authClient auth_user_pb.AuthServiceClient) *AuthHandler {
	return &AuthHandler{authClient: authClient}
}

// Register godoc
// @Summary Регистрация пользователя
// @Description Регистрирует нового пользователя в системе
// @Tags auth
// @Accept json
// @Produce json
// @Param input body handler.AuthHandler.Register.input true "Данные для регистрации"
// @Description Поля:
// @Description - username: Логин (обязательно)
// @Description - password: Пароль (мин. 8 символов)
// @Description - email: Email (должен быть валидным)
// @Description - repeat_password: Должен совпадать с password
// @Success 200 {object} object{message=string,id=int64}
// @Failure 400 {object} object{error=string}
// @Failure 500 {object} object{error=string}
// @Router /register [post]
func (h *AuthHandler) Register(c *gin.Context) {
	var input struct {
		Username       string `json:"username"`
		Password       string `json:"password"`
		Email          string `json:"email"`
		RepeatPassword string `json:"repeat_password"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if input.Username == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Username is empty"})
		return
	}

	if input.Password == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Password is empty"})
		return
	}

	if input.RepeatPassword != input.Password {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Passwords do not match"})
		return
	}

	if input.Email == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "The email is empty"})
	}

	grpcReq := &auth_user_pb.RegisterRequest{
		Username: input.Username,
		Password: input.Password,
		Email:    input.Email,
	}

	res, err := h.authClient.Register(c, grpcReq)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if !res.Success {
		c.JSON(http.StatusBadRequest, gin.H{"error": res.Error})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "User registered successfully,",
		"id": res.Id})
}

// Login godoc
// @Summary Аутентификация пользователя
// @Description Вход пользователя в систему и получение JWT-токена
// @Tags auth
// @Accept json
// @Produce json
// @Param input body handler.AuthHandler.Login.input true "Данные для входа"
// @Description Поля:
// @Description - username: Логин (обязательно)
// @Description - password: Пароль (мин. 8 символов)
// @Description - email: Email (должен быть валидным)
// @Success 200 {object} object{token=string,message=string,id=int64}
// @Failure 400 {object} object{error=string}
// @Failure 401 {object} object{error=string}
// @Failure 500 {object} object{error=string}
// @Router /login [post]
func (h *AuthHandler) Login(c *gin.Context) {
	var input struct {
		Username string `json:"username"`
		Password string `json:"password"`
		Email    string `json:"email"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if input.Username == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Username is empty"})
		return
	}

	if input.Password == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Password is empty"})
		return
	}

	if input.Email == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "The email is empty"})
	}

	grpcReq := &auth_user_pb.LoginRequest{
		Username: input.Username,
		Password: input.Password,
		Email:    input.Email,
	}

	res, err := h.authClient.Login(c, grpcReq)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error: " + err.Error()})
		return
	}

	if !res.Success {
		c.JSON(http.StatusUnauthorized, gin.H{"error": res.Error})
		return
	}

	token, err := generateJWT(uint(res.Id))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to generate token"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"token":   token,
		"message": "Login successful",
		"id":      res.Id,
	})

}

func generateJWT(id uint) (string, error) {
	claims := jwt.MapClaims{
		"user_id": id,
		"exp":     time.Now().Add(time.Hour * 72).Unix(), // Life of token 72 hours
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtSecret)
}
