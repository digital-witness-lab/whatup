package encsqlstore

import (
	"bytes"
	"encoding/hex"
	"errors"
	"fmt"
	"math/rand"
	"regexp"
	"testing"

	"github.com/lib/pq"
)

func str2hexstr(str string) string {
    return hex.EncodeToString([]byte(str))
}

var (
    ErrNotEncrypted = errors.New("Cipher text does not represent an encrypted blob")
    TestPlaintext = []any{
        true,
        42,
        []byte("testbytes"),
        string("teststring"),
        string("plain:username"),
        string("234872938572@s.whatsapp.net"),
        string("9089034863@g.us"),
        string("1234567890:99"),
        //pq.ByteaArray([][]byte{[]byte("test1"), []byte("test2")}),
    }
    TestCipher = []any{
        true,
        42,
        []byte("enc#(testbytes)"),
        str2hexstr(string("enc#(teststring)")),
        string("plain:username"),
        string("234872938572@s.whatsapp.net"),
        string("9089034863@g.us"),
        str2hexstr("enc#(1234567890)") + ":99",
        //pq.ByteaArray([][]byte{[]byte("enc#(test1)"), []byte("enc#(test2)")}),
    }
    DecryptRegex = regexp.MustCompile(`^enc#\((.+)\)$`)
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

func (sec *StubEncContainer) EncryptString(plaintext string) (string, error) {
    ciphertext, err := sec.Encrypt([]byte(plaintext))
    if err != nil {
        return "", err
    }
    return hex.EncodeToString(ciphertext), nil
}

func (sec *StubEncContainer) decrypt(cipher []byte) ([]byte, error) {
    if match := DecryptRegex.FindSubmatch(cipher); match != nil {
        return match[1], nil
    }
    return nil, ErrNotEncrypted
}

func (sec *StubEncContainer) decryptString(ciphertext string) (string, error) {
    ciphertextBytes, err := hex.DecodeString(ciphertext)
    if err != nil {
        return "", err
    }
    plaintextBytes, err := sec.decrypt(ciphertextBytes)
    if err != nil {
        return "", err
    }
    return string(plaintextBytes), nil
}

func StubDBMethod(query string, args ...any) ([]any, error) {
    return args, nil
}

type StubScannable struct {
}

func (ss *StubScannable) Scan(dest ...any) error {
    return nil
}

var letterRunes = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

func RandString(n int) string {
    b := make([]rune, n)
    for i := range b {
        b[i] = letterRunes[rand.Intn(len(letterRunes))]
    }
    return string(b)
}

func TestEncryptBytes(t *testing.T) {
    ec, err := NewWithDB(nil, "", nil).WithCredentials("username", "passphrase")
    if err != nil {
        t.Fatalf("Could not add credentials to container: %v", err)
    }
    for i := 0; i < 100; i++ {
        plain := make([]byte, 32)
        rand.Read(plain)
        cipher, err := ec.Encrypt(plain)
        if err != nil {
            t.Fatalf("Could not encrypt: %s", err)
        }
        plainCheck, err := ec.decrypt(cipher)
        if err != nil {
            t.Fatalf("Could not decrypt: %s", err)
        }
        if len(plain) != len(plainCheck) || !bytes.Equal(plain, plainCheck) {
            t.Fatalf("Enc/Dec didn't yield same byte slice")
        }
    }
}

func TestEncryptStrings(t *testing.T) {
    ec, err := NewWithDB(nil, "", nil).WithCredentials("username", "passphrase")
    if err != nil {
        t.Fatalf("Could not add credentials to container: %v", err)
    }
    for i := 0; i < 100; i++ {
        plain := RandString(32)
        cipher, err := ec.EncryptString(plain)
        if err != nil {
            t.Fatalf("Could not encrypt: %s", err)
        }
        plainCheck, err := ec.decryptString(cipher)
        if err != nil {
            t.Fatalf("Could not decrypt: %s", err)
        }
        if len(plain) != len(plainCheck) || plain != plainCheck {
            t.Fatalf("Enc/Dec didn't yield same byte slice")
        }
    }
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

    output := make([]any, len(TestCipher))
    copy(output, TestCipher)
    dests := make([]any, len(output))
    for i := range(output) {
        dests[i] = &output[i]
    }

    stubScannable := &StubScannable{}
    err = decryptDBScan(sec, stubScannable, dests...)
    if err != nil {
        t.Fatalf("Error running DB decryption: %v", err)
    }

    CompareResults(t, TestPlaintext, output)
}
