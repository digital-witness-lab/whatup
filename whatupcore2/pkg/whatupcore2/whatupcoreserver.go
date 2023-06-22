package whatupcore2

import (
	"context"
	"fmt"

	pb "github.com/digital-witness-lab/whatup/protos"
	"google.golang.org/protobuf/types/known/timestamppb"
)

type WhatUpCoreServer struct {
    sessionManager *SessionManager
    pb.UnimplementedWhatUpCoreServer
}

func (s *WhatUpCoreServer) GetConnectionStatus(ctx context.Context, credentials *pb.ConnectionStatusOptions) (*pb.ConnectionStatus, error) {
    session, ok := ctx.Value("session").(*Session)
    if !ok {
        return nil, fmt.Errorf("Could not extract session from context")
    }

    return &pb.ConnectionStatus{
        IsConnected: session.Client.IsConnected(),
        IsLoggedIn: session.Client.IsLoggedIn(),
        Timestamp: timestamppb.New(session.Client.LastSuccessfulConnect),
    }, nil
}
