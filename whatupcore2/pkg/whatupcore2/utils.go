package whatupcore2

import (
	"reflect"

	"github.com/nyaruka/phonenumbers"
)

<<<<<<< HEAD
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

func mergeGroupParticipants(participants []types.GroupParticipant, jids []types.JID) []types.GroupParticipant {
	participantsFull := make([]types.GroupParticipant, len(participants))
	seenJids := make(map[string]bool)
	for _, jid := range jids {
		seenJids[jid.String()] = false
	}

	for i, participant := range participants {
		pJID := participant.JID
		seenJids[pJID.String()] = true
		participantsFull[i] = participant
	}

	for jids, seen := range seenJids {
		if !seen {
			jid, _ := types.ParseJID(jids)
			participant := types.GroupParticipant{
				JID: jid,
			}
			participantsFull = append(participantsFull, participant)
		}
	}
	return participantsFull
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
		Agent:  uint32(JID.ActualAgent()),
		Device: uint32(JID.Device),
		Server: JID.Server,
	}
}

func ProtoToJID(pJID *pb.JID) types.JID {
	return types.JID{
		User:     pJID.User,
		RawAgent: uint8(pJID.Agent),
		Device:   uint16(pJID.Device),
		Server:   pJID.Server,
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
		OwnerJID:  JIDToProto(gi.OwnerJID),

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
		ParentJID:               JIDToProto(gi.LinkedParentJID),
		MemberAddMode:           string(gi.MemberAddMode),
		IsLocked:                gi.IsLocked,
		IsAnnounce:              gi.IsAnnounce,
		IsEphemeral:             gi.IsEphemeral,
		IsIncognito:             gi.IsIncognito,
		IsCommunityDefaultGroup: gi.IsDefaultSubGroup,

		ParticipantVersionId: gi.ParticipantVersionID,
		Participants:         participants,
=======
func UserToCountry(user string) string {
	num, err := phonenumbers.Parse("+"+user, "IN")
	if err != nil {
		return ""
>>>>>>> main
	}
	return phonenumbers.GetRegionCodeForNumber(num)
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

func valueToBytes(value reflect.Value) (result []byte) {
	for value.Kind() == reflect.Ptr {
		value = value.Elem()
	}
	defer func() {
		if p := recover(); p != nil {
			result = []byte{}
		}
	}()
	return value.Bytes()

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
	seenAddr := make(map[uintptr]bool)
	for len(queue) > 0 {
		v := queue[0]
		queue = queue[1:]
		for v.Kind() == reflect.Ptr && v.IsValid() {
			output = append(output, action(v)...)
			v = v.Elem()
		}
		if !v.IsValid() {
			continue
		}
		if p := uintptr(v.UnsafeAddr()); !seenAddr[p] {
			seenAddr[p] = true
			switch v.Kind() {
			case reflect.Struct:
				output = append(output, action(v)...)
				for i := 0; i < v.NumField(); i++ {
					queue = append(queue, v.Field(i))
				}
			case reflect.Slice, reflect.Array:
				output = append(output, action(v)...)
				for i := 0; i < v.Len(); i++ {
					queue = append(queue, v.Index(i))
				}
			}
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

func getEnvAsBoolean(value string) bool {
	return value == "true"
}
