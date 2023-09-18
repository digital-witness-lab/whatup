package whatupcore2

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"fmt"
	"reflect"
	"strings"

	pb "github.com/digital-witness-lab/whatup/protos"
	waProto "go.mau.fi/whatsmeow/binary/proto"
	"go.mau.fi/whatsmeow/types"
)

var (
    ANON_KEY = []byte("71b8e9c8f7ca3b00936f62db2e2593fd6abd74dd743453e188b7aa7075b8f991")
    ANON_VERSION = "v001"
    REDACT_FIELDS = [...]string{"FullName", "FirstName", "PushName"}
)


func redactJID(JID *pb.JID) *pb.JID {
    if !strings.HasPrefix(JID.User, "anon.") && (JID.Server == types.DefaultUserServer || JID.Server == types.LegacyUserServer) {
        JID.User = anonymizeString(JID.User)
        JID.IsAnonymized = true
        JID.UserGeocode = UserToCountry(JID.User)
    }
    return JID
}


func RedactInterface[T any](object T) T {
    findRunAction(object, func(value reflect.Value) []reflect.Value {
        if value.CanInterface() {
            if JID, ok := value.Interface().(*pb.JID); ok {
                redactJID(JID)
            } else if extText, ok := value.Interface().(*waProto.ExtendedTextMessage); ok && extText != nil {
                text := *extText.Text
                if mentionedJids := extText.GetContextInfo().GetMentionedJid(); mentionedJids != nil {
                    newMentioned := make([]string, len(mentionedJids))
                    for i, jid := range mentionedJids {
                        if user, rest, found := strings.Cut(jid, "@"); found {
                            anonUser := anonymizeString(user)
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
            for _, fieldName := range REDACT_FIELDS {
                if field := value.FieldByName(fieldName); field.IsValid() && field.CanSet() {
                    field.SetString(anonymizeString(field.String()))
                }
            }
		}
        return nil
    })
    return object
}


func anonymizeString(user string) string {
	if user == "" {
		return ""
    } else if strings.HasPrefix(user, "anon.") {
        return user
    }
	mac := hmac.New(sha256.New, ANON_KEY)
	mac.Write([]byte(user))
	return fmt.Sprintf("anon.%s.%s", base64.RawURLEncoding.EncodeToString(mac.Sum(nil)), ANON_VERSION)
}

