package whatupcore2

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"fmt"
	"reflect"
	"strings"
	"sync"

	pb "github.com/digital-witness-lab/whatup/protos"
	waProto "go.mau.fi/whatsmeow/binary/proto"
	"go.mau.fi/whatsmeow/types"
)

var (
	_ANON_KEY        = []byte("71b8e9c8f7ca3b00936f62db2e2593fd6abd74dd743453e188b7aa7075b8f991")
	ANON_VERSION     = "v001"
	ANONYMIZE_FIELDS = [...]string{"FullName", "FirstName", "PushName"}
)

func AnonymizeString(user string) string {
	if user == "" {
		return ""
	} else if strings.HasPrefix(user, "anon.") {
		return user
	}
	mac := hmac.New(sha256.New, _ANON_KEY)
	mac.Write([]byte(user))
	return fmt.Sprintf("anon.%s.%s", base64.RawURLEncoding.EncodeToString(mac.Sum(nil)), ANON_VERSION)
}

type AnonLookup struct {
	client  *WhatsAppClient
	lookup  sync.Map
	isReady bool
}

func NewAnonLookup(client *WhatsAppClient) *AnonLookup {
	return &AnonLookup{client: client}
}

func NewAnonLookupEmpty() *AnonLookup {
	return &AnonLookup{client: nil, isReady: true}
}

func (al *AnonLookup) makeReady() bool {
	if al.isReady {
		return true
	}
	contacts, err := al.client.Store.Contacts.GetAllContacts()
	if err != nil {
		al.client.Log.Errorf("Could not get contacts to initialize anon lookup: %v", err)
		return false
	}
	for jid := range contacts {
		anonUser := AnonymizeString(jid.User)
		al.lookup.Store(anonUser, jid.User)
	}
	al.isReady = true
	return true
}

func (al *AnonLookup) setAnon(anon string, clear string) bool {
	if !al.makeReady() {
		return false
	}
	al.lookup.Store(anon, clear)
	return true
}

func (al *AnonLookup) DeAnonString(anonString string) (string, bool) {
	if !al.makeReady() {
		return "", false
	}
	clear, found := al.lookup.Load(anonString)
	return clear.(string), found
}

func (al *AnonLookup) anonymizeJIDProto(JID *pb.JID) *pb.JID {
	if JID == nil {
        return JID
    }
	if !strings.HasPrefix(JID.GetUser(), "anon.") && (JID.GetServer() == types.DefaultUserServer || JID.GetServer() == types.LegacyUserServer) {
		anonUser := AnonymizeString(JID.User)
		user := JID.User
		al.setAnon(anonUser, JID.User)
		JID.User = anonUser
		JID.IsAnonymized = true
		JID.UserGeocode = UserToCountry(user)
	}
	return JID
}

func (al *AnonLookup) deAnonymizeJIDProto(JID *pb.JID) (*pb.JID, bool) {
	if strings.HasPrefix(JID.User, "anon.") {
		user, found := al.lookup.Load(JID.User)
		if found {
			JID.User = user.(string)
			JID.IsAnonymized = false
			return JID, true
		}
		return JID, false
	}
	return JID, true
}

func AnonymizeInterface[T any](al *AnonLookup, object T) T {
	findRunAction(object, func(value reflect.Value) []reflect.Value {
		if value.CanInterface() {
			if JID, ok := value.Interface().(*pb.JID); ok {
				al.anonymizeJIDProto(JID)
			} else if extText, ok := value.Interface().(*waProto.ExtendedTextMessage); ok && extText != nil {
				text := *extText.Text
				if mentionedJids := extText.GetContextInfo().GetMentionedJid(); mentionedJids != nil {
					newMentioned := make([]string, len(mentionedJids))
					for i, jid := range mentionedJids {
						if user, rest, found := strings.Cut(jid, "@"); found {
							anonUser := AnonymizeString(user)
							al.setAnon(anonUser, user)
							text = strings.ReplaceAll(text, user, anonUser)
							newMentioned[i] = anonUser + rest
						}
					}
					extText.Text = &text
					any(object).(*pb.WUMessage).Content.Text = text
					extText.ContextInfo.MentionedJid = newMentioned
				}
			}
		}
		if value.Kind() == reflect.Struct {
			for _, fieldName := range ANONYMIZE_FIELDS {
				if field := value.FieldByName(fieldName); field.IsValid() && field.CanSet() {
					field.SetString(AnonymizeString(field.String()))
				}
			}
		}
		return nil
	})
	return object
}

func DeAnonymizeInterface[T any](al *AnonLookup, object T) T {
	findRunAction(object, func(value reflect.Value) []reflect.Value {
		if value.CanInterface() {
			if JID, ok := value.Interface().(*pb.JID); ok {
				al.deAnonymizeJIDProto(JID)
			}
		}
		return nil
	})
	return object
}
