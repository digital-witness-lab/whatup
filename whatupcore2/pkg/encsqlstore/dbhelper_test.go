package encsqlstore

import (
	"bytes"
	"database/sql"
	"encoding/hex"
	"errors"
	"fmt"
	"math/rand"
	"regexp"
	"testing"

	"github.com/google/uuid"
	"github.com/lib/pq"
	"go.mau.fi/whatsmeow/types"
	waLog "go.mau.fi/whatsmeow/util/log"
)

func str2hexstr(str string) string {
	return hex.EncodeToString([]byte(str))
}

var (
	UUID, err       = uuid.NewRandom()
	log             = waLog.Stdout("dbhelper_test", "DEBUG", true)
	ErrNotEncrypted = errors.New("Cipher text does not represent an encrypted blob")
	TestPlaintext   = []any{
		true,
		42,
		[]byte("testbytes"),
		string("teststring"),
		string("plain:username"),
		string("234872938572@s.whatsapp.net"),
		string("9089034863@g.us"),
		string("1234567890:99"),
		sql.NullString{String: "teststring", Valid: true},
		pq.ByteaArray([][]byte{[]byte("test1"), []byte("test2")}),
		UUID,
	}
	TestCipher = []any{
		true,
		42,
		[]byte("enc#(testbytes)"),
		str2hexstr("enc#(teststring)"),
		string("plain:username"),
		str2hexstr("enc#(234872938572@s.whatsapp.net)"),
		str2hexstr("enc#(9089034863@g.us)"),
		str2hexstr("enc#(1234567890)") + ":99",
		sql.NullString{String: str2hexstr("enc#(teststring)"), Valid: true},
		pq.ByteaArray([][]byte{[]byte("enc#(test1)"), []byte("enc#(test2)")}),
		UUID,
	}
	DecryptRegex = regexp.MustCompile(`^enc#\((.+)\)$`)
)

func CompareResults(t *testing.T, expected, found []any) {
	for i, item := range expected {
		t.Logf("Comparing results for type %T. Wanted %s. Got %s", item, item, found[i])
		CompareResult(t, item, found[i])
	}
}

func CompareResult(t *testing.T, item, foundValue any) {
	switch expectedValue := item.(type) {
	case bool:
		if expectedValue != foundValue {
			t.Fatalf("Didn't find expected found for %T: %v != %v", expectedValue, foundValue, expectedValue)
		}
	case string:
		if expectedValue != foundValue {
			t.Fatalf("Didn't find expected found for %T: %s != %s", expectedValue, foundValue, expectedValue)
		}
	case []byte:
		if !bytes.Equal(expectedValue, foundValue.([]byte)) {
			t.Fatalf("Didn't find expected found for %T: %s != %s", expectedValue, foundValue, expectedValue)
		}
	case sql.NullString:
		foundNullString := foundValue.(sql.NullString)
		if expectedValue.String != foundNullString.String {
			t.Fatalf("Didn't find expected found for %T: %s != %s", expectedValue, foundNullString.String, expectedValue.String)
		}
	case pq.ByteaArray:
		foundBytea := foundValue.(pq.ByteaArray)
		if len(foundBytea) != len(expectedValue) {
			t.Fatalf("Didn't find correct array length for %T: %v != %v", expectedValue, foundValue, expectedValue)
		}
		for j := 0; j < len(expectedValue); j += 1 {
			if !bytes.Equal(expectedValue[j], foundBytea[j]) {
				t.Fatalf("Didn't find expected found for %T: %v != %v", expectedValue, foundValue, expectedValue)
			}
		}
	}
}

type StubEncContainer struct {
	*EncContainer
}

func NewStubEncContainer() *StubEncContainer {
	ec := NewWithDB(nil, "dialect", log)
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

func TestEncryptBytesDeterministic(t *testing.T) {
	ec, err := NewWithDB(nil, "", log).WithCredentials("username", "passphrase")
	if err != nil {
		t.Fatalf("Could not add credentials to container: %v", err)
	}
	plain := []byte("TESTTEST")
	cipher1, err := ec.Encrypt(plain)
	if err != nil {
		t.Fatalf("Could not encrypt: %s", err)
	}
	cipher2, err := ec.Encrypt(plain)
	if err != nil {
		t.Fatalf("Could not encrypt: %s", err)
	}
	if !bytes.Equal(cipher1, cipher2) {
		t.Fatalf("Enc/Dec didn't yield same byte slice")
	}
}

func TestEncryptStringDeterministic(t *testing.T) {
	ec, err := NewWithDB(nil, "", log).WithCredentials("username", "passphrase")
	if err != nil {
		t.Fatalf("Could not add credentials to container: %v", err)
	}
	plain := string("TESTTEST")
	cipher1, err := ec.EncryptString(plain)
	if err != nil {
		t.Fatalf("Could not encrypt: %s", err)
	}
	cipher2, err := ec.EncryptString(plain)
	if err != nil {
		t.Fatalf("Could not encrypt: %s", err)
	}
	if cipher1 != cipher2 {
		t.Fatalf("Enc/Dec didn't yield same byte slice")
	}
}

func TestEncryptBytes(t *testing.T) {
	ec, err := NewWithDB(nil, "", log).WithCredentials("username", "passphrase")
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
	ec, err := NewWithDB(nil, "", log).WithCredentials("username", "passphrase")
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
	if !bytes.Equal(result, []byte("enc#(TEST)")) {
		t.Fatalf("Incorrect stub encryption result: %s", result)
	}
}

func TestEncryptDBArguments(t *testing.T) {
	sec, err := StubEncContainerWithCredentials("username", "passphrase")
	if err != nil {
		t.Fatalf("Could not add credentials to container: %v", err)
	}

	output, err := encryptQueryRows(sec, StubDBMethod, "", TestPlaintext...)
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
	for i, value := range TestCipher {
		switch v := value.(type) {
		// I wish i didn't need this switch that runs the same exact code,
		// but everything i try doing sends a *interface{} to the decrypt
		// function and this seemed to work.... *shrug*
		case []byte:
			err = decryptDBScan(sec, stubScannable, &v)
			CompareResult(t, TestPlaintext[i], v)
		case string:
			err = decryptDBScan(sec, stubScannable, &v)
			CompareResult(t, TestPlaintext[i], v)
		case bool:
			err = decryptDBScan(sec, stubScannable, &v)
			CompareResult(t, TestPlaintext[i], v)
		case int:
			err = decryptDBScan(sec, stubScannable, &v)
			CompareResult(t, TestPlaintext[i], v)
		case sql.NullString:
			err = decryptDBScan(sec, stubScannable, &v)
			CompareResult(t, TestPlaintext[i], v)
		case pq.ByteaArray:
			err = decryptDBScan(sec, stubScannable, &v)
			CompareResult(t, TestPlaintext[i], v)
		}
		if err != nil {
			t.Fatalf("Error running DB decryption: %v", err)
		}
	}
}

func TestDecryptDBArgumentsJID(t *testing.T) {
	ec, err := NewWithDB(nil, "", log).WithCredentials("username", "passphrase")
	if err != nil {
		t.Fatalf("Could not add credentials to container: %v", err)
	}

	JIDValue := "1234@s.whatssapp.net"
	stubScannable := &StubScannable{}
	encrypted, err := encryptQueryRows(ec, StubDBMethod, "", JIDValue)
	if err != nil {
		t.Fatalf("Could not encrypt JID value: %v", err)
	}
	jid := &types.JID{}
	jid.Scan(encrypted[0])
	if err != nil {
		t.Fatalf("Could not parse encrypted JID: %v", err)
	}
	err = decryptDBScan(ec, stubScannable, &jid)
	if err != nil {
		t.Fatalf("Could not decrypt JID: %v", err)
	}

	if jid.String() != JIDValue {
		t.Fatalf("Scanning string JID field into types.JID failed: %s != %s", jid.String(), JIDValue)
	}
}
