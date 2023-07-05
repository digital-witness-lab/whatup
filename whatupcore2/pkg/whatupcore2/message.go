package whatupcore2

import (
	"errors"
	"fmt"
	"reflect"
	"strings"
	"time"

	pb "github.com/digital-witness-lab/whatup/protos"
	"go.mau.fi/whatsmeow"
	waProto "go.mau.fi/whatsmeow/binary/proto"
	"go.mau.fi/whatsmeow/types"
	"go.mau.fi/whatsmeow/types/events"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/protobuf/types/known/timestamppb"
)

var (
	ErrNoThumnails = errors.New("No thumbnail found")
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

func NewMessageFromWhatsMeow(client *WhatsAppClient, m *events.Message) (*Message, error) {
	msgId := m.Info.ID
	return &Message{
		client:  client,
		log:     waLog.Stdout(fmt.Sprintf("Message: %s", msgId), "DEBUG", true),
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
    if m == nil {
        return nil
    }
	switch {
	case m.GetImageMessage() != nil:
		return m.GetImageMessage()
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
	case m.GetAudioMessage() != nil:
		return m.GetReactionMessage()
	default:
		return nil
	}
}

func (msg *Message) downloadableMessageToMediaMessage(extMessage interface{}) *pb.MediaMessage {
	// WARNING: this method will remove the JpegThumbnail field from the original message
	if extMessage == nil {
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
	case *waProto.ReactionMessage:
		mediaMessage.Payload = &pb.MediaMessage_ReactionMessage{ReactionMessage: v}
	default:
		msg.log.Debugf("Could not determine type for: %s", reflect.TypeOf(extMessage))
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
	return strings.Join(texts, "; ")
}

func (msg *Message) MessageText() string {
	return msg.MessageFieldsToStr([]string{"Conversation", "Caption", "Text"})
}

func (msg *Message) MessageTitle() string {
	return msg.MessageFieldsToStr([]string{"Title"})
}

func (msg *Message) GetLink() string {
	return msg.MessageEvent.Message.GetExtendedTextMessage().GetCanonicalUrl()
}

func (msg *Message) IsInvite() bool {
    return msg.MessageEvent.Message.GetExtendedTextMessage().GetInviteLinkGroupTypeV2() > 0
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

func (msg *Message) getThumbnail(extMessage interface{}) ([]byte, error) {
    thumbnailMsg, ok := extMessage.(whatsmeow.DownloadableThumbnail)
    if !ok {
        return nil, ErrNoThumnails
    }
	thumbnail, err := msg.client.DownloadThumbnail(thumbnailMsg)
	if err == nil {
		return thumbnail, err
	}
	if msgThumbnail, ok := extMessage.(HasJpegThumbnail); ok {
		thumbnail := msgThumbnail.GetJpegThumbnail()
		return thumbnail, nil
	}
	return nil, ErrNoThumnails
}

func (msg *Message) ToProto() (*pb.WUMessage, bool) {
	// Docs that were useful for doing this:
	//
	// https://github.com/tulir/whatsmeow/blob/12cd3cdb2257c2f87a520b6b90dfd43c5fd1b36c/types/events/events.go#L226
	// https://github.com/tulir/whatsmeow/blob/12cd3cdb2257c2f87a520b6b90dfd43c5fd1b36c/mdtest/main.go#L793
	var (
		thumbnail      []byte
		forwardedScore uint32
		isForwarded    bool
		mediaMessage   *pb.MediaMessage
		err            error
	)

	extMessage := msg.GetExtendedMessage()
	if extMessage != nil {
		forwardedScore, isForwarded = msg.getForwardedScore(extMessage)
		thumbnail, err = msg.getThumbnail(extMessage)
		mediaMessage = msg.downloadableMessageToMediaMessage(extMessage)
		if err != nil {
			msg.log.Errorf("Could not download thumbnail: %v", err)
		}
	}

	return &pb.WUMessage{
		Content: &pb.MessageContent{
			Title:        msg.MessageTitle(),
			Text:         msg.MessageText(),
			Link:         msg.GetLink(),
			Thumbnail:    thumbnail,
			MediaMessage: mediaMessage,
		},
		Info: &pb.MessageInfo{
			Source: &pb.MessageSource{
				Chat:               JIDToProto(msg.Info.Chat),
				Sender:             JIDToProto(msg.Info.Sender),
				BroadcastListOwner: JIDToProto(msg.Info.BroadcastListOwner),
				IsFromMe:           msg.Info.IsFromMe,
				IsGroup:            msg.Info.IsGroup,
			},
			Timestamp: timestamppb.New(msg.Info.Timestamp),
			Id:        msg.Info.ID,
			PushName:  msg.Info.PushName,
			Type:      msg.Info.Type,
			Category:  msg.Info.Category,
			Multicast: msg.Info.Multicast,
		},
		MessageProperties: &pb.MessageProperties{
			IsEphemeral:           msg.IsEphemeral,
			IsViewOnce:            msg.IsViewOnce,
			IsDocumentWithCaption: msg.IsDocumentWithCaption,
			IsEdit:                msg.IsEdit,
            IsInvite:              msg.IsInvite(),
			IsForwarded:           isForwarded,
			ForwardedScore:        forwardedScore,
		},
        OriginalMessage: msg.MessageEvent.Message,
	}, true
}
