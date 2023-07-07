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
	waProto "go.mau.fi/whatsmeow/binary/proto"
	"go.mau.fi/whatsmeow/store"
	"go.mau.fi/whatsmeow/store/sqlstore"
	"go.mau.fi/whatsmeow/types"
	"go.mau.fi/whatsmeow/types/events"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/protobuf/proto"
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

	historyMessages chan *Message
	presenceHandler uint32
	dbPath          string
}

func NewWhatsAppClient(username string, passphrase string) (*WhatsAppClient, error) {
	store.DeviceProps.RequireFullSync = proto.Bool(true)
	store.DeviceProps.HistorySyncConfig = &waProto.DeviceProps_HistorySyncConfig{
		FullSyncDaysLimit:   proto.Uint32(365 * 3),
		FullSyncSizeMbLimit: proto.Uint32((1 << 32) - 1),
		StorageQuotaMb:      proto.Uint32((1 << 32) - 1),
	}

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
		Client:          wmClient,
		dbPath:          dbPath,
		historyMessages: make(chan *Message, 32),
	}
	client.presenceHandler = wmClient.AddEventHandler(client.setConnectPresence)

	return client, nil
}

func (wac *WhatsAppClient) setConnectPresence(evt interface{}) {
	switch evt.(type) {
	case events.Connected:
		err := wac.SendPresence(types.PresenceAvailable)
		if err != nil {
			wac.Log.Errorf("Could not send presence: %+v", err)
		}
	}
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

	historyCtx, historyCtxClose := context.WithCancel(context.Background())
	go wac.fillHistoryMessages(historyCtx)

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
					wac.Log.Infof("No login detected. deleting temporary DB file: %s", wac.dbPath)
					wac.cleanupDBFile()
					historyCtxClose()
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
				state.Errors <- fmt.Errorf("Unknown event during login: %v: %s", evt.Code, evt.Event)
				return false
			}
		case <-ctx.Done():
			return false
		}
	}
}

func (wac *WhatsAppClient) GetMessages(ctx context.Context) chan *Message {
	msgChan := make(chan *Message)
	handlerId := wac.AddEventHandler(func(evt interface{}) {
		switch wmMsg := evt.(type) {
		case *events.Message:
			msg, err := NewMessageFromWhatsMeow(wac, wmMsg)
			if err != nil {
				return
			}
			msgChan <- msg
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

func (wac *WhatsAppClient) fillHistoryMessages(ctx context.Context) {
	handlerId := wac.AddEventHandler(func(evt interface{}) {
		switch message := evt.(type) {
		case *events.HistorySync:
			wac.Log.Infof("History Progress: %d", message.Data.GetProgress())
			for _, conv := range message.Data.GetConversations() {
				jid, err := types.ParseJID(conv.GetId())
				if err != nil {
					wac.Log.Errorf("Error parsing JID from history: %v", err)
					continue
				} else if jid.Server == types.BroadcastServer || jid.Server == types.HiddenUserServer {
					wac.Log.Debugf("Skipping history from JID server: %v", jid.Server)
					continue
				}

				chatJID, err := types.ParseJID(conv.GetId())
				if err != nil {
					wac.Log.Errorf("Could not get conversation JID: %v", err)
					continue
				}
				for _, rawMsg := range conv.GetMessages() {
					wmMsg, err := wac.ParseWebMessage(chatJID, rawMsg.GetMessage())
					if err != nil {
						wac.Log.Errorf("Failed to parse raw history message: %v", err)
						continue
					}

					msg, err := NewMessageFromWhatsMeow(wac, wmMsg)
					if err != nil {
						wac.Log.Errorf("Failed to convert history message: %v", err)
						continue
					}
					wac.historyMessages <- msg
				}
			}
		}
	})
	go func() {
		for range ctx.Done() {
			wac.RemoveEventHandler(handlerId)
			return
		}
	}()
	return
}

func (wac *WhatsAppClient) GetHistoryMessages(ctx context.Context) chan *Message {
	return wac.historyMessages
}

func (wac *WhatsAppClient) SendComposingPresence(jid types.JID, timeout time.Duration) {
	finishTimer := time.NewTimer(timeout)
	resendTimer := time.NewTicker(5 * time.Second)
	for {
		err := wac.Client.SendChatPresence(jid, types.ChatPresenceComposing, types.ChatPresenceMediaText)
		if err != nil {
			wac.Log.Errorf("Could not send composing presence to JID: %v: %v", jid, err)
		}
		select {
		case <-resendTimer.C:
			continue
		case <-finishTimer.C:
			resendTimer.Stop()
			err := wac.Client.SendChatPresence(jid, types.ChatPresencePaused, types.ChatPresenceMediaText)
			if err != nil {
				wac.Log.Errorf("Could not send paused presence to JID: %v: %v", jid, err)
			}
			return
		}
	}
}

/*
func (wac *WhatsAppClient) GetConversationHistory() (chan *Message, error) {
    groups, err := wac.GetJoinedGroups()
    if err != nil {
        return nil, err
    }

    chatJID, err := types.ParseJID(conv.GetId())
    for _, historyMsg := range conv.GetMessages() {
    	evt, err := wac.ParseWebMessage(chatJID, historyMsg.GetMessage())
        fmt.Println(evt)
    }
}
*/
