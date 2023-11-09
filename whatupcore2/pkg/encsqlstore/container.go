// Copyright (c) 2022 Tulir Asokan
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

package encsqlstore

import (
	"context"
	"crypto/aes"
	"crypto/cipher"
	"crypto/hmac"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"errors"
	"fmt"
	mathRand "math/rand"
	"os"

	"golang.org/x/crypto/scrypt"

	"go.mau.fi/util/random"

	waProto "go.mau.fi/whatsmeow/binary/proto"
	"go.mau.fi/whatsmeow/store"
	"go.mau.fi/whatsmeow/types"
	"go.mau.fi/whatsmeow/util/keys"
	waLog "go.mau.fi/whatsmeow/util/log"
)

var (
	ErrNoCredentials = errors.New("Container has no credentials. Cannot perform encryption tasks")
	keySalt          = []byte(os.Getenv("ENC_KEY_SALT"))
)

type EncryptableContainer interface {
	Encrypt([]byte) ([]byte, error)
	EncryptString(string) (string, error)
	HasCredentials() bool
}

type DecryptableContainer interface {
	decrypt([]byte) ([]byte, error)
	decryptString(string) (string, error)
	HasCredentials() bool
}

type scannable interface {
	Scan(dest ...interface{}) error
}

// EncContainer is a wrapper for a SQL database that can contain multiple whatsmeow sessions.
type EncContainer struct {
	db      *sql.DB
	dialect string
	log     waLog.Logger

	userContext context.Context

	DatabaseErrorHandler func(device *store.Device, action string, attemptIndex int, err error) (retry bool)
}

var _ store.DeviceContainer = (*EncContainer)(nil)

// New connects to the given SQL database and wraps it in a EncContainer.
//
// Only SQLite and Postgres are currently fully supported.
//
// The logger can be nil and will default to a no-op logger.
//
// When using SQLite, it's strongly recommended to enable foreign keys by adding `?_foreign_keys=true`:
//
//	container, err := sqlstore.New("sqlite3", "file:yoursqlitefile.db?_foreign_keys=on", nil)
func New(dialect, address string, log waLog.Logger) (*EncContainer, error) {
	db, err := sql.Open(dialect, address)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}
	container := NewWithDB(db, dialect, log)
	err = container.Upgrade()
	if err != nil {
		return nil, fmt.Errorf("failed to upgrade database: %w", err)
	}
	return container, nil
}

// NewWithDB wraps an existing SQL connection in a EncContainer.
//
// Only SQLite and Postgres are currently fully supported.
//
// The logger can be nil and will default to a no-op logger.
//
// When using SQLite, it's strongly recommended to enable foreign keys by adding `?_foreign_keys=true`:
//
//	db, err := sql.Open("sqlite3", "file:yoursqlitefile.db?_foreign_keys=on")
//	if err != nil {
//	    panic(err)
//	}
//	container := sqlstore.NewWithDB(db, "sqlite3", nil)
//
// This method does not call Upgrade automatically like New does, so you must call it yourself:
//
//	container := sqlstore.NewWithDB(...)
//	err := container.Upgrade()
func NewWithDB(db *sql.DB, dialect string, log waLog.Logger) *EncContainer {
	ec := &EncContainer{
		db:          db,
		dialect:     dialect,
		log:         log,
		userContext: context.Background(),
	}
	ec.SetLogger(log)
	return ec
}

func DeleteUsername(db *sql.DB, username string) error {
	// no encryption needed here
	_, err := db.Exec(deleteDeviceQueryUsername, username)
	return err
}

func (ec *EncContainer) WithCredentials(username, passphrase string) (*EncContainer, error) {
	key, err := scrypt.Key([]byte(passphrase), keySalt, 32768, 8, 1, 32)
	if err != nil {
		return nil, err
	}
	newEc := *ec
	c := newEc.userContext
	c = context.WithValue(c, "username", username)
	c = context.WithValue(c, "key", key)
	newEc.userContext = c
	return &newEc, nil
}

func (ec *EncContainer) SetLogger(log waLog.Logger) {
	if log == nil {
		log = waLog.Noop
	}
	ec.log = log
}

func (ec *EncContainer) HasCredentials() bool {
	return ec.userContext.Value("username") != nil && ec.userContext.Value("key") != nil
}

func (ec *EncContainer) getUsername() (string, error) {
	username := ec.userContext.Value("username").(string)
	if username == "" {
		return "", ErrNoCredentials
	}
	return username, nil
}

func (ec *EncContainer) getKey() ([]byte, error) {
	key := ec.userContext.Value("key").([]byte)
	if key == nil {
		return nil, ErrNoCredentials
	}
	return key, nil
}

func (ec *EncContainer) Encrypt(plaintext []byte) ([]byte, error) {
	key, err := ec.getKey()
	if err != nil {
		return nil, err
	}

	c, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}

	gcm, err := cipher.NewGCM(c)
	if err != nil {
		return nil, err
	}

	// We need a 12-byte nonce for GCM.
	// We use the HMAC of the given message in order to have a deterministic
	// message for proper database operation
	mac := hmac.New(sha256.New, key)
	mac.Write(plaintext)
	nonce := mac.Sum(nil)[:12]

	// ciphertext here is actually nonce+ciphertext
	// So that when we decrypt, just knowing the nonce size
	// is enough to separate it from the ciphertext.
	ciphertext := gcm.Seal(nonce, nonce, plaintext, nil)

	return append([]byte("enc:"), ciphertext...), nil
}

func (ec *EncContainer) EncryptString(plaintext string) (string, error) {
	ciphertext, err := ec.Encrypt([]byte(plaintext))
	if err != nil {
		return "", err
	}
	return hex.EncodeToString(ciphertext), nil
}

func (ec *EncContainer) decrypt(ciphertext []byte) ([]byte, error) {
	key, err := ec.getKey()
	if err != nil {
		return nil, err
	}

	c, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}

	gcm, err := cipher.NewGCM(c)
	if err != nil {
		return nil, err
	}

	// Since we know the ciphertext is actually nonce+ciphertext
	// And len(nonce) == NonceSize(). We can separate the two.
	ciphertext = ciphertext[4:] // remove "enc:" prefix
	nonceSize := gcm.NonceSize()
	nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]

	plaintext, err := gcm.Open(nil, []byte(nonce), ciphertext, nil)
	if err != nil {
		return nil, err
	}

	return plaintext, nil
}

func (ec *EncContainer) decryptString(ciphertext string) (string, error) {
	ciphertextBytes, err := hex.DecodeString(ciphertext)
	if err != nil {
		return "", err
	}
	plaintextBytes, err := ec.decrypt(ciphertextBytes)
	if err != nil {
		return "", err
	}
	return string(plaintextBytes), nil
}

const getAllDevicesQuery = `
SELECT jid, registration_id, noise_key, identity_key,
       signed_pre_key, signed_pre_key_id, signed_pre_key_sig,
       adv_key, adv_details, adv_account_sig, adv_account_sig_key, adv_device_sig,
       platform, business_name, push_name
FROM whatsmeow_enc_device
`
const getDeviceQuery = getAllDevicesQuery + " WHERE jid=$1"
const getDeviceQueryUsername = getAllDevicesQuery + " WHERE username=$1"

func (c *EncContainer) scanDevice(row scannable) (*store.Device, error) {
	var device store.Device
	device.DatabaseErrorHandler = c.DatabaseErrorHandler
	device.Log = c.log
	device.SignedPreKey = &keys.PreKey{}
	var noisePriv, identityPriv, preKeyPriv, preKeySig []byte
	var account waProto.ADVSignedDeviceIdentity

	fmt.Println("About to decrypt device request")
	err := decryptDBScan(c, row,
		&device.ID, &device.RegistrationID, &noisePriv, &identityPriv,
		&preKeyPriv, &device.SignedPreKey.KeyID, &preKeySig,
		&device.AdvSecretKey, &account.Details, &account.AccountSignature, &account.AccountSignatureKey, &account.DeviceSignature,
		&device.Platform, &device.BusinessName, &device.PushName)
	if err != nil {
		return nil, fmt.Errorf("failed to scan session: %w", err)
	} else if len(noisePriv) != 32 || len(identityPriv) != 32 || len(preKeyPriv) != 32 || len(preKeySig) != 64 {
		c.log.Errorf("Scanned device has wrong key lengths: %s", noisePriv)
		return nil, ErrInvalidLength
	}

	device.NoiseKey = keys.NewKeyPairFromPrivateKey(*(*[32]byte)(noisePriv))
	device.IdentityKey = keys.NewKeyPairFromPrivateKey(*(*[32]byte)(identityPriv))
	device.SignedPreKey.KeyPair = *keys.NewKeyPairFromPrivateKey(*(*[32]byte)(preKeyPriv))
	device.SignedPreKey.Signature = (*[64]byte)(preKeySig)
	device.Account = &account

	innerStore := NewEncSQLStore(c, *device.ID)
	device.Identities = innerStore
	device.Sessions = innerStore
	device.PreKeys = innerStore
	device.SenderKeys = innerStore
	device.AppStateKeys = innerStore
	device.AppState = innerStore
	device.Contacts = innerStore
	device.ChatSettings = innerStore
	device.MsgSecrets = innerStore
	device.PrivacyTokens = innerStore
	device.Container = c
	device.Initialized = true

	return &device, nil
}

// GetDevice finds the device with the specified JID in the database.
//
// If the device is not found, nil is returned instead.
//
// Note that the parameter usually must be an AD-JID.
func (c *EncContainer) GetDevice(jid types.JID) (*store.Device, error) {
	sess, err := c.scanDevice(encryptQueryRow(c, c.db.QueryRow, getDeviceQuery, jid))
	if errors.Is(err, sql.ErrNoRows) {
		return nil, nil
	}
	return sess, err
}

func (c *EncContainer) GetDeviceUsername(username string) (*store.Device, error) {
	sess, err := c.scanDevice(encryptQueryRow(c, c.db.QueryRow, getDeviceQueryUsername, []byte("plain:"+username)))
	if errors.Is(err, sql.ErrNoRows) {
		return nil, nil
	}
	return sess, err
}

const (
	insertDeviceQuery = `
		INSERT INTO whatsmeow_enc_device (jid, username, registration_id, noise_key, identity_key,
									  signed_pre_key, signed_pre_key_id, signed_pre_key_sig,
									  adv_key, adv_details, adv_account_sig, adv_account_sig_key, adv_device_sig,
									  platform, business_name, push_name)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
		ON CONFLICT (jid) DO UPDATE
		    SET platform=excluded.platform, business_name=excluded.business_name, push_name=excluded.push_name
	`
	deleteDeviceQuery         = `DELETE FROM whatsmeow_enc_device WHERE jid=$1`
	deleteDeviceQueryUsername = `DELETE FROM whatsmeow_enc_device WHERE username=$1`
)

// NewDevice creates a new device in this database.
//
// No data is actually stored before Save is called. However, the pairing process will automatically
// call Save after a successful pairing, so you most likely don't need to call it yourself.
func (c *EncContainer) NewDevice() *store.Device {
	device := &store.Device{
		Log:       c.log,
		Container: c,

		DatabaseErrorHandler: c.DatabaseErrorHandler,

		NoiseKey:       keys.NewKeyPair(),
		IdentityKey:    keys.NewKeyPair(),
		RegistrationID: mathRand.Uint32(),
		AdvSecretKey:   random.Bytes(32),
	}
	device.SignedPreKey = device.IdentityKey.CreateSignedPreKey(1)
	return device
}

// ErrDeviceIDMustBeSet is the error returned by PutDevice if you try to save a device before knowing its JID.
var ErrDeviceIDMustBeSet = errors.New("device JID must be known before accessing database")

// PutDevice stores the given device in this database. This should be called through Device.Save()
// (which usually doesn't need to be called manually, as the library does that automatically when relevant).
func (c *EncContainer) PutDevice(device *store.Device) error {
	if device.ID == nil {
		return ErrDeviceIDMustBeSet
	}
	username, err := c.getUsername()
	if err != nil {
		return ErrNoCredentials
	}
	_, err = encryptQueryRows(c, c.db.Exec,
		insertDeviceQuery,
		device.ID.String(),
		[]byte("plain:"+username),
		device.RegistrationID,
		device.NoiseKey.Priv[:],
		device.IdentityKey.Priv[:],
		device.SignedPreKey.Priv[:],
		device.SignedPreKey.KeyID,
		device.SignedPreKey.Signature[:],
		device.AdvSecretKey,
		device.Account.Details,
		device.Account.AccountSignature,
		device.Account.AccountSignatureKey,
		device.Account.DeviceSignature,
		device.Platform,
		device.BusinessName,
		device.PushName,
	)

	if !device.Initialized {
		innerStore := NewEncSQLStore(c, *device.ID)
		device.Identities = innerStore
		device.Sessions = innerStore
		device.PreKeys = innerStore
		device.SenderKeys = innerStore
		device.AppStateKeys = innerStore
		device.AppState = innerStore
		device.Contacts = innerStore
		device.ChatSettings = innerStore
		device.MsgSecrets = innerStore
		device.PrivacyTokens = innerStore
		device.Initialized = true
	}
	return err
}

// DeleteDevice deletes the given device from this database. This should be called through Device.Delete()
func (c *EncContainer) DeleteDevice(store *store.Device) error {
	if store.ID == nil {
		return ErrDeviceIDMustBeSet
	}
	_, err := encryptQueryRows(c, c.db.Exec, deleteDeviceQuery, store.ID.String())
	return err
}
