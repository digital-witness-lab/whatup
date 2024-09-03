package whatupcore2

import (
	"fmt"
	"math/rand"
	"os"
	"reflect"
	"time"

	"github.com/nyaruka/phonenumbers"
	"go.mau.fi/whatsmeow/types"
	"golang.org/x/exp/constraints"
)

func durationWithJitter(baseDuration time.Duration, jitterPercent float64) time.Duration {
	jitter := time.Duration(rand.Float64()*2-1) * time.Duration(float64(baseDuration)*jitterPercent)
    duration := baseDuration + jitter
	if duration < time.Second {
		duration = time.Second
	}
    return duration
}

func rateLimit(ml *MutexMap, key string, duration time.Duration) Unlocker {
	locker := ml.Lock(key)
	go func() {
		time.Sleep(duration)
		locker.Unlock()
	}()
	return locker
}

func mergeGroupParticipants(participants []types.GroupParticipant, jids []types.JID) []types.GroupParticipant {
	participantsFull := make([]types.GroupParticipant, len(participants))
	seenJids := make(map[string]bool)
	for _, jid := range jids {
		seenJids[jid.String()] = false
	}

	for i, participant := range participants {
		seenJids[participant.JID.String()] = true
		seenJids[participant.LID.String()] = true
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

func UserToCountry(user string) string {
	num, err := phonenumbers.Parse("+"+user, "IN")
	if err != nil {
		return ""
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

func mustGetEnv(key string) string {
	value, found := os.LookupEnv(key)
	if !found {
		panic(fmt.Sprintf("Could not find required envvar: %s", key))
	}
	return value
}

func min[T constraints.Ordered](a, b T) T {
	if a < b {
		return a
	}
	return b
}
