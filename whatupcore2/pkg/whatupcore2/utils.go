package whatupcore2

import (
	"reflect"

	pb "github.com/digital-witness-lab/whatup/protos"
	"go.mau.fi/whatsmeow/types"
	"go.mau.fi/whatsmeow/store"
	"google.golang.org/protobuf/types/known/timestamppb"
)

func MessageInfoToProto(info types.MessageInfo, contactStore store.ContactStore) *pb.MessageInfo {
    return &pb.MessageInfo{
        Source: MessageSourceToProto(info.MessageSource, contactStore),
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
        Timestamp: mi.Timestamp.AsTime(),
        ID:        mi.Id,
        PushName:  mi.PushName,
        Type:      mi.Type,
        Category:  mi.Category,
        Multicast: mi.Multicast,
    }
}

func MessageSourceToProto(source types.MessageSource, contactStore store.ContactStore) *pb.MessageSource {
    contact, _ := contactStore.GetContact(source.Sender)
    return &pb.MessageSource{
        Chat:               JIDToProto(source.Chat),
        Sender:             JIDToProto(source.Sender),
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
        FirstName: contact.FirstName,
        FullName: contact.FullName,
        PushName: contact.PushName,
        BusinessName: contact.BusinessName,
    }
}

func GroupInfoToProto(gi *types.GroupInfo, contactStore store.ContactStore) *pb.GroupInfo {
	participants := make([]*pb.GroupParticipant, len(gi.Participants))
	for i, p := range gi.Participants {
        contact, _ := contactStore.GetContact(p.JID)
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

func valuesFilterZero(values []reflect.Value) []reflect.Value {
	filtered := make([]reflect.Value, 0, len(values))
	for _, item := range values {
		for item.Kind() == reflect.Ptr {
			item = item.Elem()
		}
		if !item.IsZero() {
			filtered = append(filtered, item)
		}
	}
	return filtered
}

func valueToType(value reflect.Value) interface{} {
    vp := reflect.New(value.Type())
    vp.Elem().Set(value)
    return vp.Interface()
}

func valuesToType(values []reflect.Value) []interface{} {
	interfaces := make([]interface{}, len(values))
	for i, value := range values {
		interfaces[i] = valueToType(value)
	}
	return interfaces
}

func valuesToStrings(values []reflect.Value) []string {
	strings := make([]string, len(values))
	for i, value := range values {
		for value.Kind() == reflect.Ptr {
			value = value.Elem()
		}
		strings[i] = value.String()
	}
	return strings
}

func findRunAction(v interface{}, action func(reflect.Value) []reflect.Value) []reflect.Value {
	output := []reflect.Value{}
	queue := []reflect.Value{reflect.ValueOf(v)}
	for len(queue) > 0 {
		v := queue[0]
		queue = queue[1:]
		for v.Kind() == reflect.Ptr {
			output = append(output, action(v)...)
			v = v.Elem()
		}
		if v.Kind() != reflect.Struct {
			continue
		}
		output = append(output, action(v)...)
		for i := 0; i < v.NumField(); i++ {
			queue = append(queue, v.Field(i))
		}
	}
	return output
}

func findFuncCall(input interface{}, funcName string) []reflect.Value {
	return findRunAction(input, func(field reflect.Value) []reflect.Value {
		if f := field.MethodByName(funcName); f.IsValid() {
			return f.Call([]reflect.Value{})
		}
		return nil
	})
}

func findFieldName(input interface{}, fieldName string) []reflect.Value {
	return findRunAction(input, func(field reflect.Value) []reflect.Value {
		if field.Kind() != reflect.Struct {
			return nil
		}
		if f := field.FieldByName(fieldName); f.IsValid() && !f.IsZero() {
			return []reflect.Value{f}
		}
		return nil
	})
}

func findFieldNameFunc(input interface{}, fieldFunc func(string) bool) []reflect.Value {
	return findRunAction(input, func(field reflect.Value) []reflect.Value {
		if field.Kind() != reflect.Struct {
			return nil
		}
		if f := field.FieldByNameFunc(fieldFunc); f.IsValid() && !f.IsZero() {
			return []reflect.Value{f}
		}
		return nil
	})
}
