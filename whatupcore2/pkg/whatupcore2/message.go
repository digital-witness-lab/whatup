package whatupcore2

import (
	"errors"
	"fmt"
	"time"

	pb "github.com/digital-witness-lab/whatup/protos"
	"go.mau.fi/whatsmeow"
	waProto "go.mau.fi/whatsmeow/binary/proto"
	"go.mau.fi/whatsmeow/types"
	"go.mau.fi/whatsmeow/types/events"
	waLog "go.mau.fi/whatsmeow/util/log"
)

var (
	ErrNoThumbnails = errors.New("No thumbnail found")
)

type HasContextInfo interface {
	GetContextInfo() *waProto.ContextInfo
}

type HasJpegThumbnail interface {
	GetJpegThumbnail() []byte
}

type MessageEvent = events.Message

type Message struct {
	client *WhatsAppClient
	log    waLog.Logger
	*MessageEvent
}

func MessageHasContent(m *events.Message) bool {
	// This is a place to filter out protocol messages that would otherwise seep to the bots
	if m.RawMessage.GetSenderKeyDistributionMessage() != nil {
		return false
	}
	return true
}

func NewMessageFromWhatsMeow(client *WhatsAppClient, m *events.Message) (*Message, error) {
	msgId := m.Info.ID
	return &Message{
		client:       client,
		log:          client.Log.Sub(fmt.Sprintf("Message/%s", msgId)),
		MessageEvent: m,
	}, nil
}

func (msg *Message) MarkRead() error {
	now := time.Now()
	msg.log.Debugf("Marking message as read")
	var sender types.JID
	if msg.Info.IsGroup {
		sender = msg.Info.Sender
	}
	return msg.client.MarkRead(
		[]types.MessageID{msg.Info.ID},
		now,
		msg.Info.Chat,
		sender,
	)
}

func (msg *Message) GetExtendedMessage() interface{} {
	if msg == nil {
		return nil
	}
	m := msg.MessageEvent.Message
	switch {
	case m.GetImageMessage() != nil:
		return m.GetImageMessage()
	case m.GetPtvMessage() != nil:
		return m.GetPtvMessage()
	case m.GetVideoMessage() != nil:
		return m.GetVideoMessage()
	case m.GetAudioMessage() != nil:
		return m.GetAudioMessage()
	case m.GetDocumentMessage() != nil:
		return m.GetDocumentMessage()
	case m.GetStickerMessage() != nil:
		return m.GetStickerMessage()
	case m.GetExtendedTextMessage() != nil:
		return m.GetExtendedTextMessage()
	case m.GetReactionMessage() != nil:
		return m.GetReactionMessage()
	case m.GetProtocolMessage() != nil:
		return m.GetProtocolMessage()
	default:
		return nil
	}
}

func (msg *Message) downloadableMessageToMediaMessage(extMessage interface{}) *pb.MediaMessage {
	// WARNING: this method will remove the JpegThumbnail field from the original message
	if extMessage == nil {
		return nil
	}
	_, canDownload := extMessage.(whatsmeow.DownloadableMessage)
	if !canDownload {
		return nil
	}

	mediaMessage := &pb.MediaMessage{}
	switch v := extMessage.(type) {
	case *waProto.ImageMessage:
		v.JpegThumbnail = nil
		mediaMessage.Payload = &pb.MediaMessage_ImageMessage{ImageMessage: v}
	case *waProto.VideoMessage:
		v.JpegThumbnail = nil
		mediaMessage.Payload = &pb.MediaMessage_VideoMessage{VideoMessage: v}
	case *waProto.AudioMessage:
		mediaMessage.Payload = &pb.MediaMessage_AudioMessage{AudioMessage: v}
	case *waProto.DocumentMessage:
		v.JpegThumbnail = nil
		mediaMessage.Payload = &pb.MediaMessage_DocumentMessage{DocumentMessage: v}
	case *waProto.StickerMessage:
		mediaMessage.Payload = &pb.MediaMessage_StickerMessage{StickerMessage: v}
	default:
		if canDownload {
			msg.log.Warnf("Downloadable message not handled by WhatUpCore2: %T", v)
		}
		return nil
	}
	return mediaMessage
}

func (msg *Message) MessageFieldsToStr(fields []string) string {
	values := findFieldNameFunc(msg.MessageEvent.Message,
		func(field string) bool {
			for _, f := range fields {
				if f == field {
					return true
				}
			}
			return false
		})
	texts := valuesToStrings(valuesFilterZero(values))
	if len(texts) > 0 {
		return texts[0]
	}
	return ""
}

func (msg *Message) MessageText() string {
	return msg.MessageFieldsToStr([]string{"Conversation", "Caption", "Text"})
}

func (msg *Message) MessageTitle() string {
	return msg.MessageFieldsToStr([]string{"Title"})
}

func (msg *Message) GetLink() string {
	return msg.MessageFieldsToStr([]string{"CanonicalUrl"})
}

func (msg *Message) IsReaction() bool {
	return msg.MessageEvent.Info.Type == "reaction"
}

func (msg *Message) IsInvite() bool {
	invite_link := false
	if msg.MessageEvent.Message.GetExtendedTextMessage() != nil {
		invite_link = (msg.MessageEvent.Message.GetExtendedTextMessage().InviteLinkGroupTypeV2 != nil)
	}

	return (invite_link || msg.MessageEvent.Message.GetGroupInviteMessage() != nil)
}

func (msg *Message) IsDelete() bool {
	if m := msg.MessageEvent.Message.GetProtocolMessage(); m != nil {
		return m.GetType() == waProto.ProtocolMessage_REVOKE
	}
	return false
}

func (msg *Message) GetContextInfo() (*waProto.ContextInfo, bool) {
	return msg.getContextInfo(msg.GetExtendedMessage())
}

func (msg *Message) getContextInfo(extMessage interface{}) (*waProto.ContextInfo, bool) {
	if msgContext, ok := extMessage.(HasContextInfo); ok {
		return msgContext.GetContextInfo(), true
	}
	return nil, false
}

func (msg *Message) GetForwardedScore() (uint32, bool) {
	return msg.getForwardedScore(msg.GetExtendedMessage())
}

func (msg *Message) getForwardedScore(extMessage interface{}) (uint32, bool) {
	if contextInfo, ok := msg.getContextInfo(extMessage); ok {
		return uint32(contextInfo.GetForwardingScore()), contextInfo.GetIsForwarded()
	}
	return 0, false
}

func (msg *Message) GetThumbnail() ([]byte, error) {
	return msg.getThumbnail(msg.GetExtendedMessage())
}

func (msg *Message) GetReferenceMessageId() (string, bool) {
	return msg.getReferenceMessageId(msg.GetExtendedMessage())
}

func (msg *Message) getReferenceMessageId(extMessage interface{}) (string, bool) {
	if extMessage == nil {
		return "", false
	}
	switch v := extMessage.(type) {
	case *waProto.ReactionMessage:
		return v.GetKey().GetId(), true
	case *waProto.ExtendedTextMessage:
		return v.GetContextInfo().GetStanzaId(), true
	case *waProto.ProtocolMessage:
		return v.GetKey().GetId(), true
	default:
		return "", false
	}
}

func (msg *Message) getThumbnail(extMessage interface{}) ([]byte, error) {
	thumbnailMsg, ok := extMessage.(whatsmeow.DownloadableThumbnail)
	if !ok {
		return nil, ErrNoThumbnails
	}
	thumbnail, err := msg.client.DownloadThumbnail(thumbnailMsg)
	if err == nil {
		return thumbnail, err
	}
	if msgThumbnail, ok := extMessage.(HasJpegThumbnail); ok {
		thumbnail := msgThumbnail.GetJpegThumbnail()
		return thumbnail, nil
	}
	return nil, ErrNoThumbnails
}

func (msg *Message) ToProto() (*pb.WUMessage, bool) {
	// Docs that were useful for doing this:
	//
	// https://github.com/tulir/whatsmeow/blob/12cd3cdb2257c2f87a520b6b90dfd43c5fd1b36c/types/events/events.go#L226
	// https://github.com/tulir/whatsmeow/blob/12cd3cdb2257c2f87a520b6b90dfd43c5fd1b36c/mdtest/main.go#L793
	var (
		thumbnail       []byte
		forwardedScore  uint32
		isForwarded     bool
		mediaMessage    *pb.MediaMessage
		err             error
		inReferenceToId string
	)

	extMessage := msg.GetExtendedMessage()
	if extMessage != nil {
		forwardedScore, isForwarded = msg.getForwardedScore(extMessage)
		thumbnail, err = msg.getThumbnail(extMessage)
		if err != nil && err != ErrNoThumbnails {
			msg.log.Errorf("Could not download thumbnail: %v", err)
		}
		mediaMessage = msg.downloadableMessageToMediaMessage(extMessage)
		inReferenceToId, _ = msg.getReferenceMessageId(extMessage)
	}

	protoMsg := &pb.WUMessage{
		Content: &pb.MessageContent{
			Title:           msg.MessageTitle(),
			Text:            msg.MessageText(),
			Link:            msg.GetLink(),
			Thumbnail:       thumbnail,
			MediaMessage:    mediaMessage,
			InReferenceToId: inReferenceToId,
		},
		Info: MessageInfoToProto(msg.Info, msg.client.Store),
		MessageProperties: &pb.MessageProperties{
			IsEphemeral:           msg.IsEphemeral,
			IsViewOnce:            msg.IsViewOnce,
			IsDocumentWithCaption: msg.IsDocumentWithCaption,
			IsEdit:                msg.IsEdit,
			IsDelete:              msg.IsDelete(),
			IsInvite:              msg.IsInvite(),
			IsForwarded:           isForwarded,
			IsReaction:            msg.IsReaction(),
			IsMedia:               mediaMessage != nil,
			ForwardedScore:        forwardedScore,
		},
		Provenance: map[string]string{
			"whatupcore__version":   WhatUpCoreVersion,
			"whatupcore__timestamp": time.Now().Format(time.RFC3339),
		},
		OriginalMessage: msg.MessageEvent.Message,
	}
	return protoMsg, true
}

func (msg *Message) DebugString() string {
	if msg == nil {
		return "[nil msg]"
	}
	return fmt.Sprintf("[%s @ %s] %s => %s", msg.Info.ID, msg.Info.Timestamp, msg.Info.Sender.String(), msg.Info.Chat.String())
}
