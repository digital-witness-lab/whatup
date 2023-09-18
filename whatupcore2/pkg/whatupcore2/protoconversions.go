package whatupcore2

import (
	pb "github.com/digital-witness-lab/whatup/protos"
	"go.mau.fi/whatsmeow"
	"go.mau.fi/whatsmeow/store"
	"go.mau.fi/whatsmeow/types"
	"google.golang.org/protobuf/types/known/timestamppb"
)

func ProtoToMediaType(mediaType pb.SendMessageMedia_MediaType) (whatsmeow.MediaType, bool) {
	switch m := mediaType.String(); m {
	case "MediaImage":
		return whatsmeow.MediaImage, true
	case "MediaVideo":
		return whatsmeow.MediaVideo, true
	case "MediaAudio":
		return whatsmeow.MediaAudio, true
	case "MediaDocument":
		return whatsmeow.MediaDocument, true
	}
	return "", false
}

func MessageInfoToProto(info types.MessageInfo, device *store.Device) *pb.MessageInfo {
	return &pb.MessageInfo{
		Source:    MessageSourceToProto(info.MessageSource, device),
		Timestamp: timestamppb.New(info.Timestamp),
		Id:        info.ID,
		PushName:  info.PushName,
		Type:      info.Type,
		Category:  info.Category,
		Multicast: info.Multicast,
	}
}

func ProtoToMessageInfo(mi *pb.MessageInfo) types.MessageInfo {
	return types.MessageInfo{
		MessageSource: ProtoToMessageSource(mi.Source),
		Timestamp:     mi.Timestamp.AsTime(),
		ID:            mi.Id,
		PushName:      mi.PushName,
		Type:          mi.Type,
		Category:      mi.Category,
		Multicast:     mi.Multicast,
	}
}

func MessageSourceToProto(source types.MessageSource, device *store.Device) *pb.MessageSource {
	contact, _ := device.Contacts.GetContact(source.Sender)
	return &pb.MessageSource{
		Chat:               JIDToProto(source.Chat),
		Sender:             JIDToProto(source.Sender),
        Reciever:           JIDToProto(*device.ID),
		SenderContact:      ContactToProto(&contact),
		BroadcastListOwner: JIDToProto(source.BroadcastListOwner),
		IsFromMe:           source.IsFromMe,
		IsGroup:            source.IsGroup,
	}
}

func ProtoToMessageSource(ms *pb.MessageSource) types.MessageSource {
	return types.MessageSource{
		Chat:               ProtoToJID(ms.Chat),
		Sender:             ProtoToJID(ms.Sender),
		BroadcastListOwner: ProtoToJID(ms.BroadcastListOwner),
		IsFromMe:           ms.IsFromMe,
		IsGroup:            ms.IsGroup,
	}
}


func JIDToProto(JID types.JID) *pb.JID {
	return &pb.JID{
		User:   JID.User,
		Agent:  uint32(JID.Agent),
		Device: uint32(JID.Device),
		Server: JID.Server,
		Ad:     JID.AD,
	}
}

func ProtoToJID(pJID *pb.JID) types.JID {
	return types.JID{
		User:   pJID.User,
		Agent:  uint8(pJID.Agent),
		Device: uint8(pJID.Device),
		Server: pJID.Server,
		AD:     pJID.Ad,
	}
}

func ContactToProto(contact *types.ContactInfo) *pb.Contact {
	if contact == nil || !contact.Found {
		return nil
	}
	return &pb.Contact{
		FirstName:    contact.FirstName,
		FullName:     contact.FullName,
		PushName:     contact.PushName,
		BusinessName: contact.BusinessName,
	}
}

func GroupInfoToProto(gi *types.GroupInfo, device *store.Device) *pb.GroupInfo {
	participants := make([]*pb.GroupParticipant, len(gi.Participants))
	for i, p := range gi.Participants {
		contact, _ := device.Contacts.GetContact(p.JID)
		participants[i] = &pb.GroupParticipant{
			JID:          JIDToProto(p.JID),
			Contact:      ContactToProto(&contact),
			IsAdmin:      p.IsAdmin,
			IsSuperAdmin: p.IsSuperAdmin,
			JoinError:    uint32(p.Error),
		}
	}
	return &pb.GroupInfo{
		CreatedAt: timestamppb.New(gi.GroupCreated),
		JID:       JIDToProto(gi.JID),

		GroupName: &pb.GroupName{
			Name:      gi.GroupName.Name,
			UpdatedAt: timestamppb.New(gi.GroupName.NameSetAt),
			UpdatedBy: JIDToProto(gi.GroupName.NameSetBy),
		},
		GroupTopic: &pb.GroupTopic{
			Topic:        gi.GroupTopic.Topic,
			TopicId:      gi.GroupTopic.TopicID,
			UpdatedAt:    timestamppb.New(gi.GroupTopic.TopicSetAt),
			UpdatedBy:    JIDToProto(gi.GroupTopic.TopicSetBy),
			TopicDeleted: gi.GroupTopic.TopicDeleted,
		},
		ParentJID:     JIDToProto(gi.LinkedParentJID),
		MemberAddMode: string(gi.MemberAddMode),
		IsLocked:      gi.IsLocked,
		IsAnnounce:    gi.IsAnnounce,
		IsEphemeral:   gi.IsEphemeral,

		ParticipantVersionId: gi.ParticipantVersionID,
		Participants:         participants,
	}
}
