package transport

import (
	"context"
	"errors"
	"gorm.io/gorm"
	"user_service/internal/model"
	"user_service/internal/service"
	"user_service/pkg/auth_user_pb"
)

type UserAuthServer struct {
	auth_user_pb.AuthServiceServer
	s *service.UserService
}

func NewUserAuthServer(db *gorm.DB) *UserAuthServer {
	return &UserAuthServer{
		s: service.NewUserService(db),
	}
}

func (serv *UserAuthServer) Register(ctx context.Context, req *auth_user_pb.RegisterRequest) (*auth_user_pb.RegisterResponse, error) {
	user := model.User{
		Username: req.Username,
		Password: req.Password,
		Email:    req.Email,
	}

	id, err := serv.s.CreateUser(&user)
	if err != nil {
		return &auth_user_pb.RegisterResponse{
			Success: false,
			Error:   err.Error(),
		}, nil
	}

	return &auth_user_pb.RegisterResponse{
		Id:      uint64(id),
		Success: true,
		Error:   "",
	}, nil
}

func (serv *UserAuthServer) Login(ctx context.Context, req *auth_user_pb.LoginRequest) (*auth_user_pb.LoginResponse, error) {
	user, err := serv.s.GetUserByUsername(req.Username)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return &auth_user_pb.LoginResponse{
				Success: false,
				Error:   "user not found",
			}, nil
		}
		return &auth_user_pb.LoginResponse{
			Success: false,
			Error:   err.Error(),
		}, nil
	}

	if user.Password != req.Password {
		return &auth_user_pb.LoginResponse{
			Success: false,
			Error:   "invalid password",
		}, nil
	}

	return &auth_user_pb.LoginResponse{
		Id:      uint64(user.ID),
		Success: true,
		Error:   "",
	}, nil
}
