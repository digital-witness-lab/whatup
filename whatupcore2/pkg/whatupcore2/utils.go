package whatupcore2

import (
	"reflect"

	"github.com/nyaruka/phonenumbers"
)

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
