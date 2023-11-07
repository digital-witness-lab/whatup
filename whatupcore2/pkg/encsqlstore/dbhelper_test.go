package encsqlstore

import (
	"bytes"
	"errors"
	"fmt"
	"regexp"
	"testing"

	"github.com/lib/pq"
)

var (
    ErrNotEncrypted = errors.New("Cipher text does not represent an encrypted blob")
    TestPlaintext = []any{
        true,
        []byte("testbytes"),
        string("teststring"),
        string("234872938572@s.whatsapp.net"),
        string("9089034863@g.us"),
        string("1234567890:99"),
        pq.ByteaArray([][]byte{[]byte("test1"), []byte("test2")}),
    }
    TestCipher = []any{
        true,
        []byte("enc#(testbytes)"),
        string("enc#(teststring)"),
        string("234872938572@s.whatsapp.net"),
        string("9089034863@g.us"),
        string("enc#(1234567890):99"),
        pq.ByteaArray([][]byte{[]byte("enc#(test1)"), []byte("enc#(test2)")}),
    }
    DecryptRegex = regexp.MustCompile(`^enc#\(.+\)$`)
)

func CompareResults(t *testing.T, expected, found []any) {
    for i, item := range(expected) {
        t.Logf("Comparing results for type %T. Wanted %s. Got %s", item, item, found[i])
        switch expectedValue := item.(type) {
        case bool:
            if expectedValue != found[i] {
                t.Fatalf("Didn't find expected found for %T: %v != %v", expectedValue, found[i], expectedValue)
            }
        case string:
            if expectedValue != found[i] {
                t.Fatalf("Didn't find expected found for %T: %s != %s", expectedValue, found[i], expectedValue)
            }
        case []byte:
            if !bytes.Equal(expectedValue, found[i].([]byte)) {
                t.Fatalf("Didn't find expected found for %T: %s != %s", expectedValue, found[i], expectedValue)
            }
        case pq.ByteaArray:
            foundBytea := found[i].(pq.ByteaArray)
            if len(foundBytea) != len(expectedValue) {
                t.Fatalf("Didn't find correct array length for %T: %v != %v", expectedValue, found[i], expectedValue)
            }
            for j := 0; j < len(expectedValue); j += 1 {
                if !bytes.Equal(expectedValue[j], foundBytea[j]) {
                    t.Fatalf("Didn't find expected found for %T: %v != %v", expectedValue, found[i], expectedValue)
                }
            }
        }
    }
}


type StubEncContainer struct {
    *EncContainer
}

func NewStubEncContainer() (*StubEncContainer) {
    ec := NewWithDB(nil, "dialect", nil)
    return &StubEncContainer{EncContainer: ec}
}

func StubEncContainerWithCredentials(username, passphrase string) (*StubEncContainer, error) {
    sec, err := NewStubEncContainer().WithCredentials(username, passphrase)
    if err != nil {
        return nil, err
    }
    return &StubEncContainer{EncContainer: sec}, nil
}

func (sec *StubEncContainer) Encrypt(plaintext []byte) ([]byte, error) {
    ciphertext := fmt.Sprintf("enc#(%s)", plaintext)
    return []byte(ciphertext), nil
}

func (sec *StubEncContainer) decrypt(cipher []byte) ([]byte, error) {
    if match := DecryptRegex.FindSubmatch(cipher); match != nil {
        return match[1], nil
    }
    return nil, ErrNotEncrypted
}

func StubDBMethod(query string, args ...any) ([]any, error) {
    return args, nil
}

type StubScannable struct {
}

func (ss *StubScannable) Scan(dest ...any) error {
    return nil
}


func TestSetCredentials(t *testing.T) {
    sec, err := StubEncContainerWithCredentials("username", "passphrase")
    if err != nil {
        t.Fatalf("Could not add credentials to container: %v", err)
    }

    key, err := sec.getKey()
    if err != nil {
        t.Fatalf("Could not get user key: %v", err)
    }
    if len(key) != 32 {
        t.Fatalf("User key not 32 bits long: %d", len(key))
    }
}

func TestEncryptStub(t *testing.T) {
    sec, err := StubEncContainerWithCredentials("username", "passphrase")
    if err != nil {
        t.Fatalf("Could not add credentials to container: %v", err)
    }

    result, err := sec.Encrypt([]byte("TEST"))
    if err != nil {
        t.Fatalf("Could not encrypt test string: %v", err)
    }
    if ! bytes.Equal(result, []byte("enc#(TEST)")) {
        t.Fatalf("Incorrect stub encryption result: %s", result)
    }
}


func TestEncryptDBArguments(t *testing.T) {
    sec, err := StubEncContainerWithCredentials("username", "passphrase")
    if err != nil {
        t.Fatalf("Could not add credentials to container: %v", err)
    }


    output, err := encryptDBArguments(sec, StubDBMethod, "", TestPlaintext...)
    if err != nil {
        t.Fatalf("Error running DB encryption: %v", err)
    }

    CompareResults(t, TestCipher, output)
}

func TestDecryptDBArguments(t *testing.T) {
    sec, err := StubEncContainerWithCredentials("username", "passphrase")
    if err != nil {
        t.Fatalf("Could not add credentials to container: %v", err)
    }


    stubScannable := &StubScannable{}
    output := make([]any, len(TestCipher))
    copy(output, TestCipher)
    t.Logf("Initial values: %s", output)
    err = decryptDBScan(sec, stubScannable, output...)
    if err != nil {
        t.Fatalf("Error running DB encryption: %v", err)
    }

    CompareResults(t, TestPlaintext, output)
}
