package encsqlstore

import (
	"fmt"
	"regexp"
	"strings"

	"github.com/lib/pq"
	"go.mau.fi/whatsmeow/types"
)

var (
	JIDServers = []string{
		types.DefaultUserServer,
		types.GroupServer,
		types.LegacyUserServer,
		types.BroadcastServer,
		types.HiddenUserServer,
		types.MessengerServer,
		types.InteropServer,
		types.NewsletterServer,
		types.HostedServer,
	}
	findAddress = regexp.MustCompile(`^(.+):([0-9]+)$`)
	findJID     = regexp.MustCompile(fmt.Sprintf(`@(%s)$`, strings.Join(JIDServers, "|")))
)

func encryptQueryRow[T any](c EncryptableContainer, dbMethod func(string, ...any) T, query string, args ...any) T {
	var zero T
	encArgs, err := encryptArguments(c, args)
	if err != nil {
		return zero
	}
	return dbMethod(query, encArgs...)
}

func encryptQueryRows[T any](c EncryptableContainer, dbMethod func(string, ...any) (T, error), query string, args ...any) (T, error) {
	var zero T
	encArgs, err := encryptArguments(c, args)
	if err != nil {
		return zero, err
	}
	return dbMethod(query, encArgs...)
}

func encryptArguments(c EncryptableContainer, args []any) ([]any, error) {
	if !c.HasCredentials() {
		return nil, ErrNoCredentials
	}

	encArgs := make([]any, len(args))
	for i, value := range args {
		var err error
		switch v := value.(type) {
		case string:
			if strings.HasPrefix(v, "plain:") {
				encArgs[i] = v
			} else if findJID.MatchString(v) {
				encArgs[i] = v
			} else if matches := findAddress.FindStringSubmatch(v); matches != nil {
				var encAddress string
				encAddress, err = c.EncryptString(matches[1])
				encArgs[i] = fmt.Sprintf("%s:%s", encAddress, matches[2])
			} else {
				var encValue string
				encValue, err = c.EncryptString(v)
				encArgs[i] = encValue
			}

		case []byte:
			var encValue []byte
			encValue, err = c.Encrypt(v)
			encArgs[i] = encValue
		case pq.ByteaArray:
			newArray := make(pq.ByteaArray, len(v))
			for i, item := range v {
				newArray[i], err = c.Encrypt(item)
				if err != nil {
					break
				}
			}
			encArgs[i] = newArray
		default:
			encArgs[i] = v
		}
		if err != nil {
			return nil, fmt.Errorf("Could not encrypt SQL argument: %+v (%T): %w", value, value, err)
		}
	}

	return encArgs, nil
}

func decryptDBScan(c DecryptableContainer, s scannable, dests ...any) error {
	err := s.Scan(dests...)
	if err != nil {
		return err
	}
	for _, dest := range dests {
		var err error
		// the problem is here with the interface dereferrence! some things
		// come in as proper *[]byte without the interface needed
		switch d := dest.(type) {
		case *[]byte:
			var plain []byte
			plain, err = c.decrypt(*d)
			*d = plain
		case *string:
			if strings.HasPrefix(*d, "plain:") {
				continue
			} else if findJID.MatchString(*d) {
				continue
			} else if matches := findAddress.FindStringSubmatch(*d); matches != nil {
				var plainAddress string
				plainAddress, err = c.decryptString(matches[1])
				if err == nil {
					plainString := fmt.Sprintf("%s:%s", plainAddress, matches[2])
					*d = plainString
				}
			} else {
				var plain string
				plain, err = c.decryptString(*d)
				if err == nil {
					*d = plain
				}
			}
		case *pq.ByteaArray:
			newArray := make(pq.ByteaArray, len(*d))
			for i, item := range *d {
				newArray[i], err = c.decrypt(item)
				if err != nil {
					break
				}
			}
			*d = newArray
		}
		if err != nil {
			return fmt.Errorf("Could not decrypt SQL scan destination: %+v (%T): %w", dest, dest, err)
		}
	}
	return nil
}
