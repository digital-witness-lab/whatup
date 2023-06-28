package whatupcore2

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"go.mau.fi/whatsmeow"
	"go.mau.fi/whatsmeow/store/sqlstore"
	"go.mau.fi/whatsmeow/types/events"
	waLog "go.mau.fi/whatsmeow/util/log"

	pb "github.com/digital-witness-lab/whatup/protos"
)

const (
	DB_ROOT         = "db"
	CONNECT_TIMEOUT = 5 * time.Second
)

type RegistrationState struct {
	QRCodes   chan string
	Errors    chan error
	Completed bool
	Success   bool
	*sync.WaitGroup
}

func NewRegistrationState() *RegistrationState {
	state := &RegistrationState{
		QRCodes:   make(chan string),
		Errors:    make(chan error),
		Completed: false,
		Success:   false,
		WaitGroup: &sync.WaitGroup{},
	}
	state.Add(1)
	return state
}

func (state *RegistrationState) Close() {
	state.Done()
	close(state.QRCodes)
	close(state.Errors)
}

func hashStringHex(unhashed string) string {
	h := sha256.New()
	h.Write([]byte(unhashed))
	hash := hex.EncodeToString(h.Sum(nil))
	return hash
}

func createDBFilePath(username string, n_subdirs int) (string, error) {
	if n_subdirs < 1 {
		return "", fmt.Errorf("n_subdirs must be >= 1: %d", n_subdirs)
	}
	path_username := filepath.Join(strings.Split(username[0:n_subdirs], "")...)
	path := filepath.Join(".", DB_ROOT, path_username)
	err := os.MkdirAll(path, 0700)
	if err != nil {
		return "", err
	}
	return filepath.Join(path, fmt.Sprintf("%s.db", username)), nil
}

type WhatsAppClient struct {
	*whatsmeow.Client

	dbPath string
}

func NewWhatsAppClient(username string, passphrase string) (*WhatsAppClient, error) {
	dbLog := waLog.Stdout("Database", "DEBUG", true)
	username_safe := hashStringHex(username)
	passphrase_safe := hashStringHex(passphrase)
	dbPath, err := createDBFilePath(username_safe, 4)
	if err != nil {
		return nil, err
	}
	dbLog.Infof("Using database file: %s", dbPath)
	dbUri := fmt.Sprintf("file:%s?_foreign_keys=on&_key=%s", dbPath, passphrase_safe)
	container, err := sqlstore.New("sqlite3", dbUri, dbLog)
	if err != nil {
		return nil, err
	}
	deviceStore, err := container.GetFirstDevice()
	if err != nil {
		return nil, err
	}
	clientLog := waLog.Stdout("Client", "DEBUG", true)
	wmClient := whatsmeow.NewClient(deviceStore, clientLog)

	wmClient.EnableAutoReconnect = true
	wmClient.EmitAppStateEventsOnFullSync = true
	wmClient.AutoTrustIdentity = true // don't do this for non-bot accounts
	wmClient.ErrorOnSubscribePresenceWithoutToken = false

	client := &WhatsAppClient{
		Client: wmClient,
		dbPath: dbPath,
	}

	return client, nil
}

func (wac *WhatsAppClient) cleanupDBFile() error {
	path := wac.dbPath
	for path != DB_ROOT && path != "." {
		err := os.Remove(path)
		if err != nil {
			return err
		}
		path = filepath.Dir(path)
	}
	return nil
}

func (wac *WhatsAppClient) IsLoggedIn() bool {
	return wac.Store.ID != nil && wac.Client.IsLoggedIn()
}

func (wac *WhatsAppClient) Login(timeout time.Duration) error {
	err := wac.Client.Connect()
	if err != nil {
		return err
	}

	if !wac.Client.WaitForConnection(timeout) {
		return whatsmeow.ErrNotLoggedIn
	}
	return nil
}

func (wac *WhatsAppClient) LoginOrRegister(ctx context.Context) *RegistrationState {
	state := NewRegistrationState()
	isNewDB := wac.Store.ID == nil

	go func(state *RegistrationState) {
		for {
			success := wac.qrCodeLoop(ctx, state)
			// we stop the registration flow if either:
			//   - there is an explicit error or timeout for registration
			//   - we sucessfully connected but the client remains not logged in
			//
			// NOTE: we could just use WaitForConnection but we also check
			//       success and IsLoggedIn to be explicit
			if !success || (success && wac.WaitForConnection(CONNECT_TIMEOUT) && wac.IsLoggedIn()) {
				state.Success = wac.IsLoggedIn()
				state.Completed = true
				wac.Log.Infof("LoginOrRegister flow complete. success = %v, completed = %v", state.Success, state.Completed)
				state.Close()
				if !wac.IsLoggedIn() && isNewDB {
					wac.Log.Infof("No login detected. deleteing temporary DB file: %s", wac.dbPath)
					wac.cleanupDBFile()
				}
				return
			}
		}
	}(state)
	return state
}

func (wac *WhatsAppClient) qrCodeLoop(ctx context.Context, state *RegistrationState) bool {
	err := wac.Connect()
	if err != nil {
		state.Errors <- err
		return false
	}
	wac.WaitForConnection(CONNECT_TIMEOUT)
	if wac.IsLoggedIn() {
		return true
	}

	wac.Log.Infof("User not logged in, starting registration flow")
	wac.Disconnect()
	inQrChan, _ := wac.GetQRChannel(context.Background())
	err = wac.Connect()
	if err != nil {
		state.Errors <- err
		return false
	}
	for {
		select {
		case evt := <-inQrChan:
			if evt.Event == "code" {
				state.QRCodes <- evt.Code
			} else if evt.Event == "success" {
				wac.Log.Debugf("Login event: %v", evt.Event)
				return true
			} else {
				wac.Log.Debugf("Unknown event: %v", evt.Event)
				state.Errors <- fmt.Errorf("Uknown event during login: %d: %s", evt.Code, evt.Event)
				return false
			}
		case <-ctx.Done():
			return false
		}
	}
}

func (wac *WhatsAppClient) GetMessages(ctx context.Context) chan *pb.WUMessage {
	msgChan := make(chan *pb.WUMessage)
	handlerId := wac.AddEventHandler(func(evt interface{}) {
		switch wmMsg := evt.(type) {
		case *events.Message:
			msg, err := NewMessageFromWhatsMeow(wac, wmMsg)
			if err != nil {
				return
			}
			if msg, ok := msg.ToProto(); ok {
				msgChan <- msg
			}
		}
	})
	go func() {
		for range ctx.Done() {
			wac.RemoveEventHandler(handlerId)
			close(msgChan)
			return
		}
	}()
	return msgChan
}
