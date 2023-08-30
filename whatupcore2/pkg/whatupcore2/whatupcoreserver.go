package whatupcore2

import (
	"context"
	"fmt"
	"net/http"
	"time"

	pb "github.com/digital-witness-lab/whatup/protos"
	"github.com/mitchellh/mapstructure"
	"go.mau.fi/whatsmeow"
	waProto "go.mau.fi/whatsmeow/binary/proto"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/timestamppb"
)

type WhatUpCoreServer struct {
	sessionManager *SessionManager
	log            waLog.Logger
	pb.UnimplementedWhatUpCoreServer
}

func prepareOutboundMediaMessage(ctx context.Context, client *WhatsAppClient, sendMessageMedia *pb.SendMessageMedia) (*waProto.Message, error) {
	mediaType, found := ProtoToMediaType(sendMessageMedia.GetMediaType())
	if !found {
		return nil, fmt.Errorf("Did not understand intended media type")
	}

	resp, err := client.Upload(ctx, sendMessageMedia.GetContent(), mediaType)
	if err != nil {
		return nil, fmt.Errorf("Could not upload message: %v", err)
	}
	var mimetype string
	if mimetype = sendMessageMedia.GetMimetype(); mimetype == "" {
		mimetype = http.DetectContentType(sendMessageMedia.GetContent())
	}
	messageData := map[string]interface{}{
		"Caption":       proto.String(sendMessageMedia.GetCaption()),
		"Mimetype":      proto.String(mimetype),
		"Url":           &resp.URL,
		"DirectPath":    &resp.DirectPath,
		"MediaKey":      resp.MediaKey,
		"FileEncSha256": resp.FileEncSHA256,
		"FileSha256":    resp.FileSHA256,
		"FileLength":    &resp.FileLength,
	}
	if title := sendMessageMedia.GetTitle(); title != "" {
		messageData["Title"] = proto.String(title)
	}
	if filename := sendMessageMedia.GetFilename(); filename != "" {
		messageData["Filename"] = proto.String(filename)
	}

	switch mediaType {
	case whatsmeow.MediaImage:
		imageMessage := &waProto.ImageMessage{}
		mapstructure.Decode(messageData, imageMessage)
		return &waProto.Message{ImageMessage: imageMessage}, nil
	case whatsmeow.MediaVideo:
		videoMessage := &waProto.VideoMessage{}
		mapstructure.Decode(messageData, videoMessage)
		return &waProto.Message{VideoMessage: videoMessage}, nil
	case whatsmeow.MediaAudio:
		audioMessage := &waProto.AudioMessage{}
		mapstructure.Decode(messageData, audioMessage)
		return &waProto.Message{AudioMessage: audioMessage}, nil
	case whatsmeow.MediaDocument:
		documentMessage := &waProto.DocumentMessage{}
		mapstructure.Decode(messageData, documentMessage)
		return &waProto.Message{DocumentMessage: documentMessage}, nil
	}
	return nil, fmt.Errorf("Could not create media message")
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

func (s *WhatUpCoreServer) SendMessage(ctx context.Context, messageOptions *pb.SendMessageOptions) (*pb.SendMessageReceipt, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}

	jid := ProtoToJID(messageOptions.Recipient)
	if messageOptions.ComposingTime > 0 {
		typingTime := time.Duration(messageOptions.ComposingTime) * time.Second
		session.Client.SendComposingPresence(jid, typingTime)
	}

	var message *waProto.Message
	switch payload := messageOptions.GetPayload().(type) {
	case *pb.SendMessageOptions_SimpleText:
		message = &waProto.Message{
			Conversation: proto.String(payload.SimpleText),
		}
	case *pb.SendMessageOptions_RawMessage:
		message = payload.RawMessage
	case *pb.SendMessageOptions_SendMessageMedia:
		var err error
		message, err = prepareOutboundMediaMessage(ctx, session.Client, payload.SendMessageMedia)
		if err != nil {
			return nil, status.Errorf(codes.Internal, "Could not prepare uploaded message: %v", err)
		}
	}

	reciept, err := session.Client.SendMessage(ctx, jid, message)
	if err != nil {
		return nil, err
	}

	recieptProto := &pb.SendMessageReceipt{
		SentAt:    timestamppb.New(reciept.Timestamp),
		MessageId: reciept.ID,
	}
	return recieptProto, nil
}

func (s *WhatUpCoreServer) SetDisappearingMessageTime(ctx context.Context, disappearingMessageOptions *pb.DisappearingMessageOptions) (*pb.DisappearingMessageResponse, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}
	var disappearingTime time.Duration
	recipient := ProtoToJID(disappearingMessageOptions.Recipient)
	autoClearTime := disappearingMessageOptions.AutoClearTime
	switch disappearingMessageOptions.DisappearingTime.String() {
	case "TIMER_OFF":
		disappearingTime = whatsmeow.DisappearingTimerOff
	case "TIMER_24HOUR":
		disappearingTime = whatsmeow.DisappearingTimer24Hours
	case "TIMER_7DAYS":
		disappearingTime = whatsmeow.DisappearingTimer7Days
	case "TIMER_90DAYS":
		disappearingTime = whatsmeow.DisappearingTimer90Days
	default:
		return nil, status.Errorf(codes.FailedPrecondition, "Invalid disappearingTime duration")
	}
	if autoClearTime > 600 {
		return nil, status.Errorf(codes.FailedPrecondition, "AutoClearTime must be less than 600 (10 minutes)")
	}

	err := session.Client.SetDisappearingTimer(recipient, disappearingTime)
	if err != nil {
		return nil, err
	}

	if autoClearTime > 0 {
		time.AfterFunc(time.Duration(autoClearTime)*time.Second, func() {
			session.Client.SetDisappearingTimer(recipient, whatsmeow.DisappearingTimerOff)
		})
	}
	return &pb.DisappearingMessageResponse{}, nil
}

func (s *WhatUpCoreServer) GetMessages(messageOptions *pb.MessagesOptions, server pb.WhatUpCore_GetMessagesServer) error {
	ctx := server.Context()
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return status.Errorf(codes.FailedPrecondition, "Could not find session")
	}

	ctx, cancel := context.WithCancel(ctx)
	defer cancel()
	msgChan := session.Client.GetMessages(ctx)

	for msg := range msgChan {
		msg.log.Debugf("Recieved message for gRPC client")
		if messageOptions.MarkMessagesRead {
			msg.MarkRead()
		}
		msgProto, ok := msg.ToProto()
		if !ok {
			msg.log.Errorf("Could not convert message to WUMessage proto: %v", msg)
		} else if err := server.Send(msgProto); err != nil {
			s.log.Errorf("Could not send message to client: %v", err)
			return nil
		}
	}
	session.log.Debugf("Ending GetMessages")
	return nil
}

func (s *WhatUpCoreServer) GetPendingHistory(historyOptions *pb.PendingHistoryOptions, server pb.WhatUpCore_GetPendingHistoryServer) error {
	ctx := server.Context()
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return status.Errorf(codes.FailedPrecondition, "Could not find session")
	}

	ctx, cancel := context.WithTimeout(ctx, time.Second*time.Duration(historyOptions.HistoryReadTimeout))
	defer cancel()
	msgChan := session.Client.GetHistoryMessages(ctx)

	for msg := range msgChan {
		msgProto, ok := msg.ToProto()
		if !ok {
			msg.log.Errorf("Could not convert message to WUMessage proto: %v", msg)
		} else if err := server.Send(msgProto); err != nil {
			return nil
		}
	}
	session.log.Debugf("Ending GetMessages")
	return nil
}

func (s *WhatUpCoreServer) DownloadMedia(ctx context.Context, downloadMediaOptions *pb.DownloadMediaOptions) (*pb.MediaContent, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}
	if downloadMediaOptions.GetInfo() == nil || downloadMediaOptions.GetMediaMessage() == nil {
		return nil, status.Errorf(codes.FailedPrecondition, "info and mediaMessage are required fields")
	}

	info := ProtoToMessageInfo(downloadMediaOptions.GetInfo())
	mediaMessage := downloadMediaOptions.GetMediaMessage()
	if mediaMessage == nil {
		return nil, status.Errorf(codes.InvalidArgument, "Message not downloadable")
	}

	body, err := session.Client.DownloadAnyRetry(ctx, mediaMessage, &info)
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
	return GroupInfoToProto(groupInfo, session.Client.Store), nil
}

func (s *WhatUpCoreServer) GetGroupInfoLink(ctx context.Context, inviteCode *pb.InviteCode) (*pb.GroupInfo, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}

	groupInfo, err := session.Client.GetGroupInfoFromLink(inviteCode.Link)
	if err != nil {
		return nil, status.Errorf(codes.Unknown, "%v", err)
	}
	return GroupInfoToProto(groupInfo, session.Client.Store), nil
}

func (s *WhatUpCoreServer) ListGroups(listGroupOptions *pb.ListGroupsOptions, server pb.WhatUpCore_ListGroupsServer) error {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return status.Errorf(codes.FailedPrecondition, "Could not find session")
	}

    joinedGroups, err := session.Client.GetJoinedGroups()
    if err != nil {
        return status.Errorf(codes.Unknown, "%v", err)
    }

    for _, groupInfo := range joinedGroups {
        groupInfoProto := GroupInfoToProto(groupInfo, session.Client.Store)
	    if err := server.Send(groupInfoProto); err != nil {
			return nil
		}
    }
    return nil
}

func (s *WhatUpCoreServer) JoinGroup(ctx context.Context, inviteCode *pb.InviteCode) (*pb.GroupInfo, error) {
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
	return GroupInfoToProto(groupInfo, session.Client.Store), nil
}
