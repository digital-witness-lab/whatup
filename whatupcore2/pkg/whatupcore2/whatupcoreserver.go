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

func (s *WhatUpCoreServer) GetMessages(messageOptions *pb.MessagesOptions, server pb.WhatUpCore_GetMessagesServer) error {
    session, ok := server.Context().Value("session").(*Session)
    if !ok {
        return fmt.Errorf("Could not extract session from context")
    }

    ctx, cancel := context.WithCancel(context.Background())
    msgChan := session.Client.GetMessages(ctx)

    for msg := range msgChan {
        if err := server.Send(msg); err != nil {
            cancel()
            return nil
        }
    }
    session.Client.Log.Debugf("Ending GetMessages")
    return nil
}
