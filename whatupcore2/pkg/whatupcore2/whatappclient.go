package whatupcore2

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
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

var (
	ErrInvalidMediaMessage = errors.New("Invalid MediaMessage")
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

func NewWhatsAppClient(username string, passphrase string, log waLog.Logger) (*WhatsAppClient, error) {
	store.SetOSInfo("WhatUp by DWL", [3]uint32{0, 1, 0})
	store.DeviceProps.RequireFullSync = proto.Bool(true)
	dbLog := log.Sub("DB")
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
	wmClient := whatsmeow.NewClient(deviceStore, log.Sub("WMC"))
	wmClient.EnableAutoReconnect = true
	wmClient.EmitAppStateEventsOnFullSync = true
	wmClient.AutoTrustIdentity = true // don't do this for non-bot accounts
	wmClient.ErrorOnSubscribePresenceWithoutToken = false

	client := &WhatsAppClient{
		Client:          wmClient,
		dbPath:          dbPath,
		historyMessages: make(chan *Message, 512),
	}
	client.presenceHandler = wmClient.AddEventHandler(client.setConnectPresence)

	return client, nil
}

func (wac *WhatsAppClient) setConnectPresence(evt interface{}) {
	switch evt.(type) {
	case events.Connected:
		wac.Log.Debugf("Setting presence and active delivery")
		err := wac.SendPresence(types.PresenceUnavailable)
		if err != nil {
			wac.Log.Errorf("Could not send presence: %+v", err)
		}
		wac.SetForceActiveDeliveryReceipts(false)
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

	historyCtx, historyCtxClose := context.WithCancel(ctx)
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
		wac.Log.Debugf("GetMessages handler got something")
		switch wmMsg := evt.(type) {
		case *events.Message:
			wac.Log.Debugf("Got new message for client")
			msg, err := NewMessageFromWhatsMeow(wac, wmMsg)
			if err != nil {
				wac.Log.Errorf("Error converting message from whatsmeow: %+v", err)
				return
			}
			wac.Log.Debugf("Sending message to client")
			msgChan <- msg
		}
	})
	go func() {
		<-ctx.Done()
		wac.Log.Debugf("GetMessages completed. Closing")
		wac.RemoveEventHandler(handlerId)
		close(msgChan)
		return
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
		default:
			wac.Log.Infof("History sync got message of type: %T", message)
		}
	})
	go func() {
		<-ctx.Done()
		wac.RemoveEventHandler(handlerId)
		return
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

func (wac *WhatsAppClient) DownloadAnyRetry(ctx context.Context, msg *waProto.Message, msgInfo *types.MessageInfo) ([]byte, error) {
	wac.Log.Debugf("Downloading message: %v", msg)
	data, err := wac.Client.DownloadAny(msg)

	if errors.Is(err, whatsmeow.ErrMediaDownloadFailedWith404) || errors.Is(err, whatsmeow.ErrMediaDownloadFailedWith410) {
		return wac.RetryDownload(ctx, msg, msgInfo)
	} else if err != nil {
		wac.Log.Errorf("Error trying to download message: %v", err)
	}
	return data, err
}

func (wac *WhatsAppClient) RetryDownload(ctx context.Context, msg *waProto.Message, msgInfo *types.MessageInfo) ([]byte, error) {
	mediaKeyCandidates := valuesFilterZero(findFieldName(msg, "MediaKey"))
	if len(mediaKeyCandidates) == 0 {
		wac.Log.Errorf("Could not find MediaKey: %+v", msg)
		return nil, ErrInvalidMediaMessage
	}
	mediaKey := valueToType(mediaKeyCandidates[0]).([]byte)
	if len(mediaKey) == 0 {
		wac.Log.Errorf("Could not convert MediaKey: %+v", msg)
		return nil, ErrInvalidMediaMessage
	}
	err := wac.Client.SendMediaRetryReceipt(msgInfo, mediaKey)
	if err != nil {
		wac.Log.Errorf("Could not send media retry: %+v", err)
		return nil, err
	}

	directPathValues := valuesFilterZero(findFieldName(msg, "DirectPath"))
	if len(directPathValues) == 0 {
		wac.Log.Errorf("Could not extract DirectPath field: %+v", msg)
		return nil, ErrInvalidMediaMessage
	}

	var body []byte
	var retryError error
	var retryWait sync.WaitGroup

	retryWait.Add(1)
	evtHandler := wac.Client.AddEventHandler(func(evt interface{}) {
		switch retry := evt.(type) {
		case *events.MediaRetry:
			if retry.MessageID == msgInfo.ID {
				retryData, err := whatsmeow.DecryptMediaRetryNotification(retry, mediaKey)
				if err != nil || retryData.GetResult() != waProto.MediaRetryNotification_SUCCESS {
					retryError = err
					retryWait.Done()
				}
				directPathValues[0].SetString(*retryData.DirectPath)
				body, retryError = wac.Client.DownloadAny(msg)
				retryWait.Done()
			}
		}
	})

	go func() {
		<-ctx.Done()
		wac.Client.RemoveEventHandler(evtHandler)
	}()

	retryWait.Wait()
	if retryError != nil {
		wac.Log.Errorf("Error in retry handler: %v", retryError)
	}
	return body, retryError
}
