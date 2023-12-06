package encsqlstore

import (
	"database/sql"
	"errors"
	"fmt"
	"regexp"
	"strings"

	"github.com/lib/pq"
	"go.mau.fi/whatsmeow/types"
)

var (
	findAddress = regexp.MustCompile(`^(.+):([0-9]+)$`)
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
			} else if matches := findAddress.FindStringSubmatch(v); matches != nil {
				var encAddress string
				encAddress, err = c.EncryptString(matches[1])
				encArgs[i] = fmt.Sprintf("%s:%s", encAddress, matches[2])
			} else {
				encArgs[i], err = c.EncryptString(v)
			}
		case types.JID:
			encArgs[i], err = c.EncryptString(v.String())
		case []byte:
			encArgs[i], err = c.Encrypt(v)
		case sql.NullString:
			encArgs[i] = v
			if v.Valid {
				var encString string
				encString, err = c.EncryptString(v.String)
				encArgs[i] = sql.NullString{
					String: encString,
					Valid:  true,
				}
			}
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

func decryptString(c DecryptableContainer, input string) (string, error) {
	if strings.HasPrefix(input, "plain:") {
		return input, nil
	} else if matches := findAddress.FindStringSubmatch(input); matches != nil {
		plainAddress, err := c.decryptString(matches[1])
		if err != nil {
			return "", err
		}
		return fmt.Sprintf("%s:%s", plainAddress, matches[2]), nil
	}
	plain, err := c.decryptString(input)
	if err != nil {
		return "", nil
	}
	return plain, nil
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
			var plain string
			plain, err = decryptString(c, *d)
			*d = plain
		case *sql.NullString:
			if d.Valid {
				var plain string
				plain, err = decryptString(c, (*d).String)
				(*d).String = plain
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
		case **types.JID:
			// When the JID was first Scan'd (types.JID.Scan), since there was
			// no @ symbol the entire encrypted blob was put in the server
			// attribute
			jidPlain, errDec := c.decryptString((*d).Server)
			jid, errParse := types.ParseJID(jidPlain)
			err = errors.Join(errDec, errParse)
			*d = &jid
		case *types.JID:
			// When the JID was first Scan'd (types.JID.Scan), since there was
			// no @ symbol the entire encrypted blob was put in the server
			// attribute
			jidPlain, errDec := c.decryptString((*d).Server)
			jid, errParse := types.ParseJID(jidPlain)
			err = errors.Join(errDec, errParse)
			*d = jid
		case *uint32:
			continue
		case *bool:
			continue
		default:
			c.Log().Debugf("Could not decrypt Scan field: %T: %+v", d, d)
		}
		if err != nil {
			return fmt.Errorf("Could not decrypt SQL scan destination: %+v (%T): %w", dest, dest, err)
		}
	}
	return nil
}
