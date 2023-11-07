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
    findJID = regexp.MustCompile(fmt.Sprintf(`@(%s)$`, strings.Join(JIDServers, "|")))
)

type Scannable interface {
    Scan(dest ...any) error
}

func encryptDBArguments[T any](c EncryptableContainer, dbMethod func(string, ...any) (T, error), query string, args ...any) (T, error) {
    var zero T
    if !c.HasCredentials() {
        return zero, ErrNoCredentials
    }

    encArgs := make([]any, len(args))
    for i, value := range(args) {
        var err error
        switch v := value.(type) {
        case string:
            if findJID.MatchString(v) {
                encArgs[i] = v
            } else
            if matches := findAddress.FindStringSubmatch(v); matches != nil {
                var encAddress []byte
                encAddress, err = c.Encrypt([]byte(matches[1]))
                encArgs[i] = fmt.Sprintf("%s:%s", encAddress, matches[2])
            } else {
                var encValue []byte
                encValue, err = c.Encrypt([]byte(v))
                encArgs[i] = string(encValue)
            }
            
        case []byte:
            var encValue []byte
            encValue, err = c.Encrypt(v)
            encArgs[i] = encValue
        case pq.ByteaArray:
            newArray := make(pq.ByteaArray, len(v))
            for i, item := range(v) {
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
            return zero, fmt.Errorf("Could not encrypt SQL argument: %+v (%T): %w", value, value, err)
        }
    }

    return dbMethod(query, encArgs...)
}

func decryptDBScan(c DecryptableContainer, scannable Scannable, dests ...any) error {
    // TODO: dests are actually a list of pointers... we need to deal with this appropriately 
    err := scannable.Scan(dests...)
    if err != nil {
        return err
    }
    for i, dest := range(dests) {
        var err error
        switch d := dest.(type) {
        case []byte:
            var plain []byte
            plain, err = c.decrypt(d)
            dests[i] = plain
        case string:
            if findJID.MatchString(d) {
                continue
            } else
            if matches := findAddress.FindAllStringSubmatch(d, -1); matches != nil {
                var plainAddress []byte
                plainAddress, err = c.decrypt([]byte(matches[0][1]))
                dests[i] = fmt.Sprintf("%s:%s", plainAddress, matches[0][2])
            } else {
                var plain []byte
                plain, err = c.decrypt([]byte(d))
                dests[i] = string(plain)
            }
        case pq.ByteaArray:
            newArray := make(pq.ByteaArray, len(d))
            for i, item := range(d) {
                newArray[i], err = c.decrypt(item)
                if err != nil {
                    break
                }
            }
            dests[i] = newArray
        default:
        }
        if err != nil {
            return fmt.Errorf("Could not decrypt SQL scan destination: %+v (%T): %w", dest, dest, err)
        }
    }
    return nil
}
