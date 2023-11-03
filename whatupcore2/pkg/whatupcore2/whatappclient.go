package whatupcore2

import (
	"context"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	pb "github.com/digital-witness-lab/whatup/protos"
	"github.com/lib/pq"
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
	HISTORY_TIMEOUT = 10 * time.Minute // time to wait for a request for history messages before getting rid of the history event handler
)

var (
	ErrInvalidMediaMessage = errors.New("Invalid MediaMessage")
	clientCreationLock     = NewMutexMap()
	appNameSuffix          = os.Getenv("APP_NAME_SUFFIX")
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

func CreateDBFilePath(username string, n_subdirs int) (string, error) {
	if n_subdirs < 1 {
		return "", fmt.Errorf("n_subdirs must be >= 1: %d", n_subdirs)
	}
	username_safe := hashStringHex(username)
	path_username := filepath.Join(strings.Split(username_safe[0:n_subdirs], "")...)
	path := filepath.Join(".", DB_ROOT, path_username)
	err := os.MkdirAll(path, 0700)
	if err != nil {
		return "", err
	}
	return filepath.Join(path, fmt.Sprintf("%s.db", username_safe)), nil
}

func ClearFileAndParents(path string) error {
	for path != DB_ROOT && path != "." {
		err := os.Remove(path)
		if err != nil {
			return err
		}
		path = filepath.Dir(path)
	}
	return nil
}

type WhatsAppClient struct {
	*whatsmeow.Client

	username              string
	historyMessages       chan *Message
	historyMessagesActive bool
	shouldRequestHistory  map[string]bool
	dbConn                *sql.DB

	aclStore *ACLStore

	presenceHandler uint32
	historyHandler  uint32
	archiveHandler  uint32

	anonLookup *AnonLookup
}

func NewWhatsAppClient(username string, passphrase string, dbUri string, log waLog.Logger) (*WhatsAppClient, error) {
	// TODO: there is a memory leak here... we need to remove unused locks that
	// haven't been used in a while
	lock := clientCreationLock.Lock(username)
	defer lock.Unlock()

	//store.SetOSInfo("Mac OS", [3]uint32{10, 15, 7})
	appName := strings.TrimSpace(fmt.Sprintf("WA by DWL %s", appNameSuffix))
	store.SetOSInfo(appName, WhatUpCoreVersionInts)
	store.DeviceProps.RequireFullSync = proto.Bool(true)
	dbLog := log.Sub("DB")
	passphrase_safe := hashStringHex(passphrase)
    if passphrase_safe == "" {
        // DELETE
    }

    sqlstore.PostgresArrayWrapper = pq.Array
	db, err := sql.Open("postgres", dbUri)
	if err != nil {
		dbLog.Errorf("Could not open database: %w", err)
		return nil, fmt.Errorf("failed to open database: %w", err)
	}
	err = db.Ping()
	if err != nil {
		dbLog.Errorf("Could not ping database: %w", err)
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	container := sqlstore.NewWithDB(db, "postgres", dbLog)
	err = container.Upgrade()
	if err != nil {
		dbLog.Errorf("Could not upgrade database: %w", err)
		return nil, fmt.Errorf("failed to upgrade database: %w", err)
	}

	deviceStore, err := container.GetFirstDevice()
	if err != nil {
		dbLog.Errorf("Could't get device from store: %w", err)
		return nil, err
	}
	wmClient := whatsmeow.NewClient(deviceStore, log.Sub("WMC"))
	wmClient.EnableAutoReconnect = true
	wmClient.EmitAppStateEventsOnFullSync = true
	wmClient.AutoTrustIdentity = true // don't do this for non-bot accounts
	wmClient.ErrorOnSubscribePresenceWithoutToken = false

	aclStore := NewACLStore(db, log.Sub("ACL"))
	client := &WhatsAppClient{
		Client:               wmClient,
		aclStore:             aclStore,
		dbConn:               db,
		username:             username,
		historyMessages:      make(chan *Message, 512),
		shouldRequestHistory: make(map[string]bool),
	}
	client.anonLookup = NewAnonLookup(client)
	client.presenceHandler = wmClient.AddEventHandler(client.setConnectPresence)
	client.historyHandler = wmClient.AddEventHandler(client.getHistorySync)
	if strings.HasSuffix(username, "-a") {
		client.Log.Warnf("HACK adding archive handler to request history on archive-state change")
		client.archiveHandler = wmClient.AddEventHandler(client.UNSAFEArchiveHack_OnArchiveGetHistory)
	}

	log.Debugf("WhatsAppClient created and lock releasing")
	return client, nil
}

func (wac *WhatsAppClient) Close() {
	wac.Log.Infof("Closing WhatsApp Client")
	wac.Disconnect()
	wac.dbConn.Close()
}

func (wac *WhatsAppClient) setConnectPresence(evt interface{}) {
	switch evt.(type) {
	case *events.Connected:
		wac.Log.Infof("Setting presence and active delivery")
		err := wac.SendPresence(types.PresenceAvailable)
		if err != nil {
			wac.Log.Errorf("Could not send presence: %+v", err)
		}
		wac.SetForceActiveDeliveryReceipts(false)
	}
}

func (wac *WhatsAppClient) removeUserDB() error {
    // TODO: figure out deleteuser
    // wac.Store.DeleteSomething(...?)
    return  nil
}

func (wac *WhatsAppClient) IsLoggedIn() bool {
	return wac.Store.ID != nil && wac.Client.IsLoggedIn()
}

func (wac *WhatsAppClient) Login(timeout time.Duration) error {
	wac.Log.Debugf("Connecting to WhatsApp from Login()")
	err := wac.Client.Connect()
	if err != nil {
		return err
	}

	if !wac.Client.WaitForConnection(timeout) {
		return whatsmeow.ErrNotLoggedIn
	}
	return nil
}

func (wac *WhatsAppClient) LoginOrRegister(ctx context.Context, registerOptions *pb.RegisterOptions) *RegistrationState {
	state := NewRegistrationState()
	isNewDB := wac.Store.ID == nil

	defaultPermission := registerOptions.DefaultGroupPermission
	wac.aclStore.SetDefault(&defaultPermission)

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
					wac.Log.Infof("No login detected. Deleting user info")
					wac.removeUserDB()
				}
				return
			}
		}
	}(state)
	return state
}

func (wac *WhatsAppClient) qrCodeLoop(ctx context.Context, state *RegistrationState) bool {
	wac.Log.Debugf("Connecting to WhatsApp from qrCodeLoop() to check login status")
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
	wac.Log.Debugf("Connecting to WhatsApp from qrCodeLoop() to start registration")
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

func (wac *WhatsAppClient) UNSAFEArchiveHack_OnArchiveGetHistory(evt interface{}) {
	switch archive := evt.(type) {
	case *events.Archive:
		if !archive.Action.GetArchived() {
			return
		}
		if !strings.HasSuffix(wac.username, "-a") {
			return
		}
		archiveJID := archive.JID.String()
		wac.Log.Warnf("HACK: new group is archived... setting shouldRequestHistory: %s", archiveJID)
		wac.shouldRequestHistory[archiveJID] = true
	}
}

func (wac *WhatsAppClient) UNSAFEArchiveHack_ShouldProcess(msg *events.Message) bool {
	if strings.HasSuffix(wac.username, "-a") {
		if !msg.Info.IsGroup {
			wac.Log.Warnf("HACK: chat not in group")
			return false
		}
		chat_jid := msg.Info.Chat
		groupSettings, err := wac.Store.ChatSettings.GetChatSettings(chat_jid)
		if err != nil {
			wac.Log.Warnf("HACK: could not get group settings: %v: %s", chat_jid, err)
			return false
		}
		if !groupSettings.Archived {
			wac.Log.Warnf("HACK: Not archived")
			return false
		}
		wac.Log.Warnf("HACK: allowing message through, archive status: %t", groupSettings.Archived)
		if wac.shouldRequestHistory[chat_jid.String()] {
			wac.Log.Warnf("HACK: requesting message history for group: %s", chat_jid.String())
			wac.RequestHistoryMsgInfo(&msg.Info)
			delete(wac.shouldRequestHistory, chat_jid.String())
		}
		return true
	}
	return true
}

func (wac *WhatsAppClient) UNSAFEArchiveHack_ShouldProcessConversation(jid *types.JID, conv *waProto.Conversation) bool {
	if strings.HasSuffix(wac.username, "-a") {
		if jid.Server != types.GroupServer {
			wac.Log.Warnf("HACK: chat not in group")
			return false
		}
		var isArchived bool = *conv.Archived
		if isArchived != true {
			wac.Log.Warnf("HACK: Not archived")
			return false
		}
		wac.Log.Warnf("HACK: allowing conversation through, archive status: %t", isArchived)
		return true
	}
	return true
}

func (wac *WhatsAppClient) GetMessages(ctx context.Context) chan *Message {
	msgChan := make(chan *Message)
	handlerId := wac.AddEventHandler(func(evt interface{}) {
		wac.Log.Debugf("GetMessages handler got something: %T", evt)
		switch wmMsg := evt.(type) {
		case *events.Message:
			aclEntry, err := wac.aclStore.GetByJID(&wmMsg.Info.Chat)
			if err != nil {
				wac.Log.Errorf("Could not read ACL for JID: %s: %+v", wmMsg.Info.Chat.String(), err)
			}
			if !aclEntry.CanRead() {
				wac.Log.Debugf("Skipping message because we don't have read permissions in group")
				return
			}
			// <HACK>
			if !wac.UNSAFEArchiveHack_ShouldProcess(wmMsg) {
				wac.Log.Warnf("HACK: skipping message")
				return
			}
			// </HACK>
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

func (wac *WhatsAppClient) getHistorySync(evt interface{}) {
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

			// <HACK>
			if !wac.UNSAFEArchiveHack_ShouldProcessConversation(&chatJID, conv) {
				wac.Log.Warnf("HACK: skipping conversation")
				continue
			}
			// </HACK>
			aclEntry, err := wac.aclStore.GetByJID(&chatJID)
			if err != nil {
				wac.Log.Errorf("Could not read ACL for JID: %s: %+v", chatJID.String(), err)
				continue
			}
			if !aclEntry.CanRead() {
				wac.Log.Debugf("Skipping message because we don't have read permissions in group")
				continue
			}

			var oldestMsgInfo *types.MessageInfo
			for _, rawMsg := range conv.GetMessages() {
				wmMsg, err := wac.ParseWebMessage(chatJID, rawMsg.GetMessage())
				if err != nil {
					wac.Log.Errorf("Failed to parse raw history message: %v", err)
					continue
				}
				if oldestMsgInfo == nil || wmMsg.Info.Timestamp.Before(oldestMsgInfo.Timestamp) {
					oldestMsgInfo = &wmMsg.Info
				}

				msg, err := NewMessageFromWhatsMeow(wac, wmMsg)
				if err != nil {
					wac.Log.Errorf("Failed to convert history message: %v", err)
					continue
				}
				wac.historyMessages <- msg
			}
			if *message.Data.SyncType == waProto.HistorySync_ON_DEMAND {
				go wac.RequestHistoryMsgInfo(oldestMsgInfo)
			}
		}
	}
}

func (wac *WhatsAppClient) RequestHistoryMsgInfo(msgInfo *types.MessageInfo) {
	wac.Log.Infof("Requesting history for group: %s", msgInfo.Chat.String())
	msg := wac.Client.BuildHistorySyncRequest(msgInfo, 50)
	// Context here should be bound to the whatsappclient's connection
	extras := whatsmeow.SendRequestExtra{Peer: true}
	wac.Client.SendMessage(context.TODO(), *wac.Client.Store.ID, msg, extras)
}

func (wac *WhatsAppClient) GetHistoryMessages(ctx context.Context) chan *Message {
	wac.historyMessagesActive = true
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
	mediaKey := valueToBytes(mediaKeyCandidates[0])
	if len(mediaKey) == 0 {
		wac.Log.Errorf("Could not convert MediaKey: %+v: %+v", msg, mediaKeyCandidates)
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
		if !wac.historyMessagesActive {
			wac.Log.Infof("Disconnecting history event handler due to inactivity")
			wac.Client.RemoveEventHandler(evtHandler)
		} else {
			wac.Log.Infof("Maintaining history event handler because of active reading")
		}
	}()

	retryWait.Wait()
	if retryError != nil {
		wac.Log.Errorf("Error in retry handler: %v", retryError)
	}
	return body, retryError
}
