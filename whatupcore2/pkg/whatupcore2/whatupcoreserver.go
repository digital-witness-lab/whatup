package whatupcore2

import (
	"context"

	pb "github.com/digital-witness-lab/whatup/protos"
	waProto "go.mau.fi/whatsmeow/binary/proto"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/timestamppb"
)

type WhatUpCoreServer struct {
	sessionManager *SessionManager
	pb.UnimplementedWhatUpCoreServer
}

func (s *WhatUpCoreServer) GetConnectionStatus(ctx context.Context, credentials *pb.ConnectionStatusOptions) (*pb.ConnectionStatus, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}

	return &pb.ConnectionStatus{
		IsConnected: session.Client.IsConnected(),
		IsLoggedIn:  session.Client.IsLoggedIn(),
		Timestamp:   timestamppb.New(session.Client.LastSuccessfulConnect),
	}, nil
}

func (s *WhatUpCoreServer) GetMessages(messageOptions *pb.MessagesOptions, server pb.WhatUpCore_GetMessagesServer) error {
	session, ok := server.Context().Value("session").(*Session)
	if !ok {
		return status.Errorf(codes.FailedPrecondition, "Could not find session")
	}

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	msgChan := session.Client.GetMessages(ctx)

	for msg := range msgChan {
		if messageOptions.MarkMessagesRead {
			msg.MarkRead()
		}
		msgProto, ok := msg.ToProto()
		if !ok {
			session.Client.Log.Errorf("Could not convert message to WUMessage proto: %v", msg)
		} else if err := server.Send(msgProto); err != nil {
			return nil
		}
	}
	session.Client.Log.Debugf("Ending GetMessages")
	return nil
}

func (s *WhatUpCoreServer) DownloadMedia(ctx context.Context, mediaMessage *waProto.Message) (*pb.MediaContent, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}

    // need to do a SendMediaRetryReceipt in some cases
    body, err := session.Client.DownloadAny(mediaMessage)
    if err != nil {
        return nil, status.Errorf(codes.Internal, "Could not download media: %v", err)
    }
    
	return &pb.MediaContent{Body: body}, nil
}

func (s *WhatUpCoreServer) GetGroupInfo(ctx context.Context, pJID *pb.JID) (*pb.GroupInfo, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}

	JID := ProtoToJID(pJID)
	groupInfo, err := session.Client.GetGroupInfo(JID)
	if err != nil {
		return nil, status.Errorf(codes.Unknown, "%v", err)
	}
	return GroupInfoToProto(groupInfo), nil
}

func (s *WhatUpCoreServer) GetGroupInfoLink(ctx context.Context,  inviteCode *pb.InviteCode) (*pb.GroupInfo, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}

	groupInfo, err := session.Client.GetGroupInfoFromLink(inviteCode.Link)
	if err != nil {
		return nil, status.Errorf(codes.Unknown, "%v", err)
	}
	return GroupInfoToProto(groupInfo), nil
}

func (s *WhatUpCoreServer) JoinGroup(ctx context.Context,  inviteCode *pb.InviteCode) (*pb.GroupInfo, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}

	groupInfo, err := session.Client.GetGroupInfoFromLink(inviteCode.Link)
	if err != nil {
        return nil, status.Errorf(codes.Unknown, "Could not get group metadata: %v", err)
	}

    _, err = session.Client.JoinGroupWithLink(inviteCode.Link)
    if err != nil {
        return nil, status.Errorf(codes.Unknown, "Could not join group: %v", err)
    }
	return GroupInfoToProto(groupInfo), nil
}
