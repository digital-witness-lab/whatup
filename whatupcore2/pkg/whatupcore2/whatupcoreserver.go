package whatupcore2

import (
	"context"
	"fmt"
	"net/http"
	"strings"
	"time"

	pb "github.com/digital-witness-lab/whatup/protos"
	"github.com/mitchellh/mapstructure"
	"go.mau.fi/whatsmeow"
	waProto "go.mau.fi/whatsmeow/binary/proto"
	"go.mau.fi/whatsmeow/types"
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

func CanReadWriteJID(session *Session, jid *types.JID) (bool, error) {
	aclEntry, err := session.Client.aclStore.GetByJID(jid)
	if err != nil {
		session.log.Errorf("Could not read ACL for JID: %+v", err)
		return false, status.Errorf(codes.Internal, "Could not read ACL: %+v", err)
	}
	if !aclEntry.CanRead() {
		session.log.Debugf("Denying request because we don't have read permissions in group")
		return false, status.Error(codes.PermissionDenied, "No read permissions to group")
	}
	if !aclEntry.CanWrite() {
		session.log.Debugf("Denying request because we don't have write permissions in group")
		return false, status.Error(codes.PermissionDenied, "No read permissions to group")
	}
	return true, nil
}

func CanWriteJID(session *Session, jid *types.JID) (bool, error) {
	aclEntry, err := session.Client.aclStore.GetByJID(jid)
	if err != nil {
		session.log.Errorf("Could not read ACL for JID: %+v", err)
		return false, status.Errorf(codes.Internal, "Could not read ACL: %+v", err)
	}
	if !aclEntry.CanWrite() {
		session.log.Debugf("Denying request because we don't have write permissions in group")
		return false, status.Error(codes.PermissionDenied, "No read permissions to group")
	}
	return true, nil
}

func CanReadJID(session *Session, jid *types.JID) (bool, error) {
	aclEntry, err := session.Client.aclStore.GetByJID(jid)
	if err != nil {
		session.log.Errorf("Could not read ACL for JID: %+v", err)
		return false, status.Errorf(codes.Internal, "Could not read ACL: %+v", err)
	}
	if !aclEntry.CanRead() {
		session.log.Debugf("Denying request because we don't have read permissions in group")
		return false, status.Error(codes.PermissionDenied, "No read permissions to group")
	}
	return true, nil
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

	var JIDProto *pb.JID
	var JIDAnnonProto *pb.JID
	if session.Client.Store.ID != nil {
		JID := *session.Client.Store.ID
		JIDProto = JIDToProto(JID)
		JIDAnnonProto = session.Client.anonLookup.anonymizeJIDProto(JIDToProto(JID))
	}
	return &pb.ConnectionStatus{
		IsConnected: session.Client.IsConnected(),
		IsLoggedIn:  session.Client.IsLoggedIn(),
		Timestamp:   timestamppb.New(session.Client.LastSuccessfulConnect),
		JID:         JIDProto,
		JIDAnon:     JIDAnnonProto,
	}, nil
}

func (s *WhatUpCoreServer) SendMessage(ctx context.Context, messageOptions *pb.SendMessageOptions) (*pb.SendMessageReceipt, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}

	messageOptions = DeAnonymizeInterface(session.Client.anonLookup, messageOptions)
	jid := ProtoToJID(messageOptions.Recipient)
	if _, err := CanWriteJID(session, &jid); err != nil {
		return nil, err
	}

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

	disappearingMessageOptions = DeAnonymizeInterface(session.Client.anonLookup, disappearingMessageOptions)
	recipient := ProtoToJID(disappearingMessageOptions.Recipient)
	if _, err := CanWriteJID(session, &recipient); err != nil {
		return nil, err
	}

	var disappearingTime time.Duration
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
	messageOptions = DeAnonymizeInterface(session.Client.anonLookup, messageOptions)

	var lastMessageTimestamp time.Time
	if messageOptions.LastMessageTimestamp != nil {
		lastMessageTimestamp = messageOptions.LastMessageTimestamp.AsTime()
	}

	ctxC := NewContextWithCancel(ctx)
	defer ctxC.Cancel()

	var heartbeatTicker *time.Ticker
	if messageOptions.HeartbeatTimeout > 0 {
		heartbeatTicker = time.NewTicker(
			time.Duration(95*messageOptions.HeartbeatTimeout/100) * time.Second,
		)
		defer heartbeatTicker.Stop()
	} else {
		heartbeatTicker = time.NewTicker(time.Second)
		heartbeatTicker.Stop()
	}
	go grpcHeartbeat(heartbeatTicker, ctxC, server)

	msgClient := session.Client.GetMessages()
	defer msgClient.Close()
	msgChan := msgClient.Receive()

	for {
		select {
		case <-ctxC.Done():
			session.log.Debugf("Client connection closed")
			return nil
		case <-session.ctxC.Done():
			session.log.Debugf("Session closed... disconnecting")
			return nil
		case msg, ok := <-msgChan:
			if !ok {
				session.log.Infof("Closing message reader because msg chan closed")
				return nil
			}
			if !lastMessageTimestamp.IsZero() {
				if !msg.Info.Timestamp.After(lastMessageTimestamp) {
					msg.log.Debugf("Skipping message because it is before client's last message: %s < %s: %s", msg.Info.Timestamp, lastMessageTimestamp, msg.DebugString())
					break
				} else {
					// once we are back in sync, reset the lastMessageTimestamp
					// var so we don't need to do time comparisons for future
					// messages
					lastMessageTimestamp = time.Time{}
				}
			}
			if messageOptions.MarkMessagesRead {
				msg.MarkRead()
			}
			msg.log.Debugf("Sending message to client: %s", msg.DebugString())
			msgProto, ok := msg.ToProto()
			if !ok {
				msg.log.Errorf("Could not convert message to WUMessage proto: %s", msg.DebugString())
				break
			}
			msgAnon := AnonymizeInterface(session.Client.anonLookup, msgProto)
			if err := server.Send(&pb.MessageStream{Content: msgAnon}); err != nil {
				s.log.Errorf("Could not send message to client: %v", err)
				return nil
			}
		}
	}
}

func (s *WhatUpCoreServer) GetPendingHistory(historyOptions *pb.PendingHistoryOptions, server pb.WhatUpCore_GetPendingHistoryServer) error {
	ctx := server.Context()
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return status.Errorf(codes.FailedPrecondition, "Could not find session")
	}
	historyOptions = DeAnonymizeInterface(session.Client.anonLookup, historyOptions)

	ctxC := NewContextWithCancel(ctx)
	defer ctxC.Cancel()

	var heartbeatTicker *time.Ticker
	if historyOptions.HeartbeatTimeout > 0 {
		heartbeatTicker = time.NewTicker(
			time.Duration(95*historyOptions.HeartbeatTimeout/100) * time.Second,
		)
		defer heartbeatTicker.Stop()
	} else {
		heartbeatTicker = time.NewTicker(time.Second)
		heartbeatTicker.Stop()
	}
	go grpcHeartbeat(heartbeatTicker, ctxC, server)

	msgClient := session.Client.GetHistoryMessages()
	defer msgClient.Close()
	msgChan := msgClient.Receive()

	for {
		select {
		case <-ctx.Done():
			session.log.Debugf("Client connection closed")
			return nil
		case <-session.ctxC.Done():
			session.log.Debugf("Session closed... disconnecting")
			return nil
		case msg, ok := <-msgChan:
			if !ok {
				session.log.Infof("Closing history reader because msg chan closed")
				return nil
			}
			msg.log.Debugf("Recieved history message for gRPC client")
			msgProto, ok := msg.ToProto()
			if !ok {
				msg.log.Errorf("Could not convert message to WUMessage proto: %s", msg.DebugString())
				break
			}
			msgAnon := AnonymizeInterface(session.Client.anonLookup, msgProto)
			if err := server.Send(&pb.MessageStream{Content: msgAnon}); err != nil {
				return nil
			}
			if historyOptions.MarkMessagesRead {
				msg.MarkRead()
			}
		}
	}
}

func (s *WhatUpCoreServer) DownloadMedia(ctx context.Context, downloadMediaOptions *pb.DownloadMediaOptions) (*pb.MediaContent, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}
	downloadMediaOptions = DeAnonymizeInterface(session.Client.anonLookup, downloadMediaOptions)

	if downloadMediaOptions.GetInfo() == nil || downloadMediaOptions.GetMediaMessage() == nil {
		return nil, status.Errorf(codes.FailedPrecondition, "info and mediaMessage are required fields")
	}

	info := ProtoToMessageInfo(downloadMediaOptions.GetInfo())
	if _, err := CanReadJID(session, &info.Chat); err != nil {
		return nil, err
	}

	mediaMessage := downloadMediaOptions.GetMediaMessage()
	if mediaMessage == nil {
		return nil, status.Errorf(codes.InvalidArgument, "Message not downloadable")
	}

	body, err := session.Client.DownloadAnyRetry(
		ctx,
		mediaMessage,
		info,
	)
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
	pJID = DeAnonymizeInterface(session.Client.anonLookup, pJID)

	JID := ProtoToJID(pJID)
	if _, err := CanReadJID(session, &JID); err != nil {
		return nil, err
	}

	groupInfo, err := session.Client.GetGroupInfo(JID)
	if err != nil {
		return nil, status.Errorf(codes.Unknown, "%v", err)
	}
	groupInfoProto := GroupInfoToProto(groupInfo, session.Client.Store)
	return AnonymizeInterface(session.Client.anonLookup, groupInfoProto), nil
}

func (s *WhatUpCoreServer) GetGroupInvite(ctx context.Context, pJID *pb.JID) (*pb.InviteCode, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}
	pJID = DeAnonymizeInterface(session.Client.anonLookup, pJID)

	JID := ProtoToJID(pJID)
	if _, err := CanReadWriteJID(session, &JID); err != nil {
		return nil, err
	}

	inviteLink, err := session.Client.GetGroupInviteLink(JID, false)
	if err != nil {
		return nil, status.Errorf(codes.Unknown, "%v", err)
	}
	groupInfoProto := &pb.InviteCode{Link: inviteLink}
	return AnonymizeInterface(session.Client.anonLookup, groupInfoProto), nil
}

func (s *WhatUpCoreServer) GetCommunityInfo(pJID *pb.JID, server pb.WhatUpCore_GetCommunityInfoServer) error {
	ctx := server.Context()
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return status.Errorf(codes.FailedPrecondition, "Could not find session")
	}
	pJID = DeAnonymizeInterface(session.Client.anonLookup, pJID)

	ctxC := NewContextWithCancel(ctx)
	defer ctxC.Cancel()

	JID := ProtoToJID(pJID)
	subgroups, err := session.Client.GetSubGroups(JID)
	if err != nil {
		return status.Errorf(codes.InvalidArgument, "Could not get community subgroups: %v", err)
	}

	communityInfo, err := session.Client.GetGroupInfo(JID)
	if err != nil {
		return status.Errorf(codes.InvalidArgument, "Could not get community metadata: %v", err)
	}
	communityParticipants, err := session.Client.GetLinkedGroupsParticipants(JID)
	if err == nil {
		communityInfo.Participants = mergeGroupParticipants(communityInfo.Participants, communityParticipants)
	}
	communityInfoProto := GroupInfoToProto(communityInfo, session.Client.Store)
	if err := server.Send(AnonymizeInterface(session.Client.anonLookup, communityInfoProto)); err != nil {
		s.log.Errorf("Could not send message to client: %v", err)
		return nil
	}

	for _, subgroup := range subgroups {
		var groupInfo *types.GroupInfo
		gJID := subgroup.JID
		can_read, _ := CanReadJID(session, &gJID)
		isPartial := false
		if can_read {
			var err error
			groupInfo, err = session.Client.GetGroupInfo(gJID)
			if err != nil {
				isPartial = true
			}
		} else {
			isPartial = true
		}
		if isPartial {
			groupInfo = &types.GroupInfo{
				JID:       gJID,
				GroupName: subgroup.GroupName,
				GroupLinkedParent: types.GroupLinkedParent{
					LinkedParentJID: JID,
				},
				GroupIsDefaultSub: types.GroupIsDefaultSub{
					IsDefaultSubGroup: subgroup.IsDefaultSubGroup,
				},
			}
		}
		groupInfoProto := GroupInfoToProto(groupInfo, session.Client.Store)
		groupInfoProto.IsPartialInfo = isPartial
		if err := server.Send(AnonymizeInterface(session.Client.anonLookup, groupInfoProto)); err != nil {
			s.log.Errorf("Could not send message to client: %v", err)
			return nil
		}
	}
	return nil
}

func (s *WhatUpCoreServer) GetGroupInfoInvite(ctx context.Context, inviteCode *pb.InviteCode) (*pb.GroupInfo, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}
	inviteCode = DeAnonymizeInterface(session.Client.anonLookup, inviteCode)

	groupInfo, err := session.Client.GetGroupInfoFromLink(inviteCode.Link)
	if err != nil {
		return nil, status.Errorf(codes.Unknown, "%v", err)
	}

	groupInfoProto := GroupInfoToProto(groupInfo, session.Client.Store)
	return AnonymizeInterface(session.Client.anonLookup, groupInfoProto), nil
}

func (s *WhatUpCoreServer) JoinGroup(ctx context.Context, inviteCode *pb.InviteCode) (*pb.GroupInfo, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}
	inviteCode = DeAnonymizeInterface(session.Client.anonLookup, inviteCode)

	groupInfo, err := session.Client.GetGroupInfoFromLink(inviteCode.Link)
	if err != nil {
		return nil, status.Errorf(codes.Unknown, "Could not get group metadata: %v", err)
	}

	_, err = session.Client.JoinGroupWithLink(inviteCode.Link)
	if err != nil {
		return nil, status.Errorf(codes.Unknown, "Could not join group: %v", err)
	}
	groupInfoProto := GroupInfoToProto(groupInfo, session.Client.Store)
	return AnonymizeInterface(session.Client.anonLookup, groupInfoProto), nil
}

func (s *WhatUpCoreServer) SetACL(ctx context.Context, groupACL *pb.GroupACL) (*pb.GroupACL, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}
	groupACL = DeAnonymizeInterface(session.Client.anonLookup, groupACL)

	aclStore := session.Client.aclStore

	jid := ProtoToJID(groupACL.JID)
	prevGroupACL, err := aclStore.GetByJID(&jid)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "Could not get ACL value: %+v", err)
	}

	if groupACL.IsDefault {
		err = aclStore.SetDefault(&groupACL.Permission)
	} else {
		err = aclStore.SetByJID(&jid, &groupACL.Permission)
	}
	if err != nil {
		return nil, status.Errorf(codes.Internal, "Could not set ACL value: %+v", err)
	}
	if strings.HasPrefix(groupACL.Permission.String(), "READ") {
		session.Client.RequestHistory(jid)
	}

	prevGroupACLProto, err := prevGroupACL.Proto()
	if err != nil {
		return prevGroupACLProto, status.Errorf(codes.Internal, "Could not convert to protobuf: %+v", err)
	}

	return AnonymizeInterface(session.Client.anonLookup, prevGroupACLProto), nil
}

func (s *WhatUpCoreServer) GetACL(ctx context.Context, jidProto *pb.JID) (*pb.GroupACL, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}

	jidProto = DeAnonymizeInterface(session.Client.anonLookup, jidProto)
	aclStore := session.Client.aclStore

	jid := ProtoToJID(jidProto)
	groupACL, err := aclStore.GetByJID(&jid)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "Could not get ACL value: %+v", err)
	}

	groupACLProto, err := groupACL.Proto()
	if err != nil {
		return groupACLProto, status.Errorf(codes.Internal, "Could not convert to protobuf: %+v", err)
	}
	return AnonymizeInterface(session.Client.anonLookup, groupACLProto), nil
}

func (s *WhatUpCoreServer) GetJoinedGroups(getJoinedGroupsOptions *pb.GetJoinedGroupsOptions, server pb.WhatUpCore_GetJoinedGroupsServer) error {
	ctx := server.Context()
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return status.Errorf(codes.FailedPrecondition, "Could not find session")
	}
	getJoinedGroupsOptions = DeAnonymizeInterface(session.Client.anonLookup, getJoinedGroupsOptions)

	defaultACL, err := session.Client.aclStore.GetDefault()
	if err != nil {
		return status.Errorf(codes.Internal, "Could not get default ACL value: %+v", err)
	}

	aclLookup, err := session.Client.aclStore.CachedLookup()
	if err != nil {
		return status.Errorf(codes.Internal, "Could not get ACL entries in lookup: %+v", err)
	}

	groupInfos, err := session.Client.GetJoinedGroups()
	if err != nil {
		return status.Errorf(codes.Internal, "Could not get joined groups: %+v", err)
	}

	for _, groupInfo := range groupInfos {
		groupInfoProto := GroupInfoToProto(groupInfo, session.Client.Store)
		aclEntry, aclFound := aclLookup.GetByJID(&groupInfo.JID)
		if !aclFound {
			aclEntry = defaultACL
		}

		aclEntryProto, err := aclEntry.Proto()
		if err != nil {
			return status.Errorf(codes.Internal, "Could not convert acl entry to proto: %+v", err)
		}

		jgProto := &pb.JoinedGroup{
			GroupInfo: groupInfoProto,
			Acl:       aclEntryProto,
		}
		jgProtoAnon := AnonymizeInterface(session.Client.anonLookup, jgProto)
		if err := server.Send(jgProtoAnon); err != nil {
			s.log.Errorf("Could not send message to client: %v", err)
			return nil
		}
	}
	return nil
}

func (s *WhatUpCoreServer) Unregister(ctx context.Context, options *pb.UnregisterOptions) (*pb.ConnectionStatus, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}
	options = DeAnonymizeInterface(session.Client.anonLookup, options)

	JID := *session.Client.Store.ID
	JIDProto := JIDToProto(JID)
	JIDAnnonProto := session.Client.anonLookup.anonymizeJIDProto(JIDToProto(JID))

	session.Client.Unregister()

	return &pb.ConnectionStatus{
		IsConnected: session.Client.IsConnected(),
		IsLoggedIn:  session.Client.IsLoggedIn(),
		Timestamp:   timestamppb.New(session.Client.LastSuccessfulConnect),
		JID:         JIDProto,
		JIDAnon:     JIDAnnonProto,
	}, nil
}

func (s *WhatUpCoreServer) RequestChatHistory(ctx context.Context, historyRequestOptions *pb.HistoryRequestOptions) (*pb.GroupInfo, error) {
	session, ok := ctx.Value("session").(*Session)
	if !ok {
		return nil, status.Errorf(codes.FailedPrecondition, "Could not find session")
	}
	historyRequestOptions = DeAnonymizeInterface(session.Client.anonLookup, historyRequestOptions)

	JID := ProtoToJID(historyRequestOptions.Chat)

	if historyRequestOptions.GetId() == "" || historyRequestOptions.GetTimestamp() == nil {
		session.Client.Log.Debugf("Requesting history messages from store")
		session.Client.RequestHistory(JID)
	} else {
		session.Client.Log.Debugf("Requesting history messages starting from requested msgID")
		lastMessage := types.MessageInfo{
			ID:        historyRequestOptions.Id,
			Timestamp: historyRequestOptions.Timestamp.AsTime(),
			MessageSource: types.MessageSource{
				Chat:     JID,
				IsFromMe: bool(historyRequestOptions.IsFromMe),
			},
		}
		session.Client.requestHistoryMsgInfoRetry(&lastMessage)
	}

	groupInfo, err := session.Client.GetGroupInfo(JID)
	if err != nil {
		return nil, status.Errorf(codes.Unknown, "%v", err)
	}
	groupInfoProto := GroupInfoToProto(groupInfo, session.Client.Store)
	return AnonymizeInterface(session.Client.anonLookup, groupInfoProto), nil
}
