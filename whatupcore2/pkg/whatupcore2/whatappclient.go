package whatupcore2

import (
	"context"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"strings"
	"sync"
	"time"
	"unicode"

	pb "github.com/digital-witness-lab/whatup/protos"
	"github.com/digital-witness-lab/whatup/whatupcore2/pkg/encsqlstore"
	"github.com/hashicorp/golang-lru/v2/expirable"
	"github.com/lib/pq"
	"go.mau.fi/whatsmeow"
	"go.mau.fi/whatsmeow/appstate"
	waProto "go.mau.fi/whatsmeow/binary/proto"
	"go.mau.fi/whatsmeow/store"
	"go.mau.fi/whatsmeow/types"
	"go.mau.fi/whatsmeow/types/events"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/protobuf/proto"
)

const (
	CONNECT_TIMEOUT = 10 * time.Second
	HISTORY_TIMEOUT = 10 * time.Minute // time to wait for a request for history messages before getting rid of the history event handler
)

var (
	ErrLoginTimeout          = errors.New("Timeout while logging in")
	ErrInvalidMediaMessage   = errors.New("Invalid MediaMessage")
	ErrDownloadRetryCanceled = errors.New("Download Retry canceled")
	ErrNoChatHistory         = errors.New("Could not find any chat history")
	appNameSuffix            = os.Getenv("APP_NAME_SUFFIX")
	loginProxy               = os.Getenv("LOGIN_PROXY")
	loginProxyFile           = os.Getenv("LOGIN_PROXY_FILE")
)
var _DeviceContainer *encsqlstore.EncContainer
var _DB *sql.DB

type RegistrationState struct {
	QRCodes   chan string
	Errors    chan error
	Completed bool
	Success   bool
	*sync.WaitGroup
}

func getDeviceContainer(dbUri string, dbLog waLog.Logger) (*encsqlstore.EncContainer, *sql.DB, error) {
	if _DeviceContainer != nil {
		return _DeviceContainer, _DB, nil
	}
	dbLog.Infof("Initializing DB Connection and global Device Store")
	encsqlstore.PostgresArrayWrapper = pq.Array
	var err error
	_DB, err = sql.Open("postgres", dbUri)
	if err != nil {
		dbLog.Errorf("Could not open database: %w", err)
		return nil, nil, fmt.Errorf("failed to open database: %w", err)
	}
	err = _DB.Ping()
	if err != nil {
		dbLog.Errorf("Could not ping database: %w", err)
		return nil, nil, fmt.Errorf("failed to open database: %w", err)
	}
	_DeviceContainer = encsqlstore.NewWithDB(_DB, "postgres", dbLog)
	return _DeviceContainer, _DB, nil
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

type WhatsAppClient struct {
	*whatsmeow.Client

	ctxC                ContextWithCancel
	username            string
	historyMessageQueue *MessageDistributor
	messageQueue        *MessageDistributor

	historyRequestContexts map[string]ContextWithCancel
	shouldRequestHistory   map[string]bool
	dbConn                 *sql.DB

	aclStore     *ACLStore
	encSQLStore  *encsqlstore.EncSQLStore
	encContainer *encsqlstore.EncContainer

	connectionHandler uint32
	historyHandler    uint32
	messageHandler    uint32
	archiveHandler    uint32

	groupInfoCache *expirable.LRU[string, *types.GroupInfo]
	mediaCache     *DiskCache
	mediaMutexMap  *MutexMap

	anonLookup *AnonLookup
}

func NewWhatsAppClient(ctx context.Context, username string, passphrase string, dbUri string, getHistory bool, log waLog.Logger) (*WhatsAppClient, error) {
	appName := strings.TrimSpace(fmt.Sprintf("WA by DWL %s", appNameSuffix))
	store.SetOSInfo(appName, WhatUpCoreVersionInts)
	store.DeviceProps.RequireFullSync = proto.Bool(getHistory)
	dbLog := log.Sub("DB")

	deviceContainer, db, err := getDeviceContainer(dbUri, dbLog)
	if err != nil {
		dbLog.Errorf("Could not create connection to DB and device container: %w", err)
		return nil, err
	}
	container, err := deviceContainer.WithCredentials(username, passphrase)
	if err != nil {
		dbLog.Errorf("Could not create encrypted SQL store: %w", err)
		return nil, fmt.Errorf("Could not create encrypted SQL store: %w", err)
	}
	container.SetLogger(dbLog)

	err = container.Upgrade()
	if err != nil {
		dbLog.Errorf("Could not upgrade database: %w", err)
		return nil, fmt.Errorf("failed to upgrade database: %w", err)
	}

	var deviceStore *store.Device
	deviceStore, err = container.GetDeviceUsername(username)
	if err != nil {
		dbLog.Errorf("Could't get device from store: %w", err)
		return nil, err
	}
	if deviceStore == nil {
		deviceStore = container.NewDevice()
	}

	wmLog := log.Sub("WMC")
	wmClient := whatsmeow.NewClient(deviceStore, wmLog)
	wmClient.EnableAutoReconnect = true
	wmClient.AutoTrustIdentity = true
	wmClient.AutomaticMessageRerequestFromPhone = true
	wmClient.EmitAppStateEventsOnFullSync = true
	wmClient.ErrorOnSubscribePresenceWithoutToken = false

	if loginProxy == "" && loginProxyFile != "" {
		buf, err := os.ReadFile(loginProxyFile)
		if err != nil {
			wmLog.Errorf("Could not open login proxy file: %s: %v", loginProxyFile, err)
			return nil, err
		}
		loginProxy = strings.TrimFunc(string(buf), unicode.IsSpace)
	}
	if loginProxy != "" {
		wmLog.Infof("Using login proxy for WM Client")
		wmClient.ToggleProxyOnlyForLogin(true)
		err = wmClient.SetProxyAddress(loginProxy, whatsmeow.SetProxyOptions{
			NoMedia: true,
		})
		if err != nil {
			wmLog.Errorf("Could not set proxy: %v", err)
			return nil, fmt.Errorf("Could not set login proxy: %v", err)
		}
	}

	ctxC := NewContextWithCancel(ctx)

	historyMessageQueue := NewMessageDistributor(NewMessageCache(16384, 10*time.Minute), log.Sub("hmq"))
	//historyMessageQueue := NewMessageQueue(ctx, time.Minute, 16384, 10*time.Minute, log.Sub("hmq"))
	//historyMessageQueue.Start()
	messageQueue := NewMessageDistributor(NewMessageCache(1024, time.Hour), log.Sub("mq"))
	//messageQueue := NewMessageQueue(ctx, time.Minute, 1024, time.Hour, log.Sub("mq"))
	//messageQueue.Start()

	aclStore := NewACLStore(db, username, log.Sub("ACL"))
	// 64 MB cache
	mediaCache, err := NewDiskCacheTempdir(ctxC, time.Minute, 64*1024*1024, time.Minute, log.Sub("mediaCache"))
	if err != nil {
		return nil, err
	}
	mediaMutexMap := NewMutexMap(log.Sub("mediaMutex"))

	client := &WhatsAppClient{
		Client: wmClient,

		ctxC:                   ctxC,
		aclStore:               aclStore,
		encContainer:           container,
		dbConn:                 db,
		username:               username,
		historyMessageQueue:    historyMessageQueue,
		messageQueue:           messageQueue,
		historyRequestContexts: make(map[string]ContextWithCancel),
		shouldRequestHistory:   make(map[string]bool),
		groupInfoCache:         expirable.NewLRU[string, *types.GroupInfo](128, nil, time.Minute),
		mediaCache:             mediaCache,
		mediaMutexMap:          mediaMutexMap,
	}
	go func() {
		<-ctx.Done()
		client.Close()
	}()
	client.anonLookup = NewAnonLookup(client)
	client.connectionHandler = wmClient.AddEventHandler(client.connectionEvents)
	client.historyHandler = wmClient.AddEventHandler(client.getHistorySync)
	client.messageHandler = wmClient.AddEventHandler(client.getMessages)

	log.Debugf("WhatsAppClient created and lock releasing")
	return client, nil
}

func (wac *WhatsAppClient) Done() <-chan struct{} {
	return wac.ctxC.Done()
}

func (wac *WhatsAppClient) Close() {
	wac.Log.Infof("Closing WhatsApp Client")
	wac.Disconnect()
	wac.ctxC.Cancel()
}

func (wac *WhatsAppClient) IsClosed() bool {
	return wac.ctxC.Err() != nil
}

func (wac *WhatsAppClient) connectionEvents(evt interface{}) {
	switch evt.(type) {
	case *events.Connected:
		wac.Log.Infof("User connected.")
		wac.encSQLStore = encsqlstore.NewEncSQLStore(wac.encContainer, *wac.Client.Store.ID)
		wac.anonLookup.makeReady()
		go wac.presenceTwiddler()
		go wac.stateReFetcher()
	case *events.LoggedOut:
		wac.Log.Warnf("User has logged out on their device")
		wac.Unregister()
		wac.encSQLStore = nil
		wac.Close()
	}
}

func (wac *WhatsAppClient) stateReFetcher() {
	ticker := time.NewTicker(24 * time.Hour)
	defer ticker.Stop()
	for {
		select {
		case <-wac.ctxC.Done():
			return
		case <-ticker.C:
			wac.Log.Infof("Refetching WhatsApp state")
			names := []appstate.WAPatchName{appstate.WAPatchRegular, appstate.WAPatchRegularHigh, appstate.WAPatchRegularLow, appstate.WAPatchCriticalUnblockLow, appstate.WAPatchCriticalBlock}
			for _, name := range names {
				wac.Log.Debugf("Refetching WhatsApp state: %s", name)
				err := wac.FetchAppState(name, true, false)
				if err != nil {
					wac.Log.Errorf("Failed to refetch WhatsApp state: %v", err)
				}
			}
		}
	}
}

func (wac *WhatsAppClient) presenceTwiddler() {
	shouldTwiddle := true

	defaultAcl, err := wac.aclStore.GetDefault()
	if err == nil && defaultAcl.CanReadWrite() {
		wac.Log.Infof("Default READ/WRITE ACL... not setting presence to unavailable ")
		shouldTwiddle = false
	} else {
		wac.Log.Infof("Default group ACL for presence twiddler: %s: %d", err, defaultAcl.Permission)
	}

	baseDuration := 30 * time.Minute
	for {
		wac.Log.Infof("Twiddling client presence ")
		wac.SendPresence(types.PresenceAvailable)
		if shouldTwiddle {
			time.Sleep(durationWithJitter(10*time.Second, 0.1))
			wac.SendPresence(types.PresenceUnavailable)
		}
		select {
		case <-wac.ctxC.Done():
			return
		case <-time.After(durationWithJitter(baseDuration, 0.25)):
			continue
		}
	}
}

func (wac *WhatsAppClient) Unregister() {
	wac.Log.Warnf("Unregistering user and clearing database!")
	wac.Logout()
	wac.Store.Delete()
	wac.aclStore.Delete()
	wac.Close()
}

func (wac *WhatsAppClient) cleanupUserDB() error {
	err_container := encsqlstore.DeleteUsername(wac.dbConn, wac.username)
	err_acl := wac.aclStore.Delete()
	return errors.Join(err_acl, err_container)
}

func (wac *WhatsAppClient) IsLoggedIn() bool {
	return wac.Store.ID != nil && wac.Client.IsLoggedIn()
}

func (wac *WhatsAppClient) Login(timeout time.Duration) error {
	wac.Log.Debugf("Connecting to WhatsApp from Login()")
	err := wac.Client.Connect()
	if err != nil {
		wac.Client.Disconnect()
		return err
	}

	if !wac.Client.WaitForConnection(timeout) {
		wac.Client.Disconnect()
		return whatsmeow.ErrNotLoggedIn
	}

	if !wac.IsLoggedIn() {
		wac.Client.Disconnect()
		return whatsmeow.ErrNotLoggedIn
	}

	return nil
}

func (wac *WhatsAppClient) LoginOrRegister(ctx context.Context, registerOptions *pb.RegisterOptions) *RegistrationState {
	state := NewRegistrationState()
	isNewDB := wac.Store.ID == nil

	defaultPermission := registerOptions.DefaultGroupPermission
	err := wac.aclStore.SetDefault(&defaultPermission)
	if err != nil {
		wac.Log.Errorf("Could not set default permission: %w", err)
		return nil
	}

	wac.Log.Debugf("Starting QR Code loop")
	go func(state *RegistrationState) {
		for {
			err, success := wac.qrCodeLoop(ctx, state)
			wac.Log.Infof("LoginOrRegister qrCodeLoop. qrErr = %w, qrSuccess = %v", err, success)

			// we stop the registration flow if either:
			//   - there is an explicit error or timeout for registration
			//   - we sucessfully connected but the client remains not logged in
			//
			// NOTE: we could just use WaitForConnection but we also check
			//       success and IsLoggedIn to be explicit
			if !success || (success && wac.WaitForConnection(2*CONNECT_TIMEOUT) && wac.IsLoggedIn()) {
				state.Success = wac.IsLoggedIn()
				state.Completed = true
				wac.Log.Infof("LoginOrRegister flow complete. success = %v, completed = %v", state.Success, state.Completed)

				state.Close()
				if !wac.IsLoggedIn() && isNewDB {
					wac.Log.Infof("No login detected. Deleting user info")
					wac.cleanupUserDB()
				}
				return
			}
		}
	}(state)
	return state
}

func (wac *WhatsAppClient) qrCodeLoop(ctx context.Context, state *RegistrationState) (error, bool) {
	wac.Log.Debugf("Connecting to WhatsApp from qrCodeLoop() to check login status")
	if !wac.IsConnected() {
		err := wac.Connect()
		if err != nil {
			state.Errors <- err
			wac.Log.Warnf("qrCodeLoop error on first connect")
			return err, false
		}
	}
	wac.WaitForConnection(CONNECT_TIMEOUT)
	if wac.IsLoggedIn() {
		return nil, true
	}

	wac.Log.Infof("User not logged in, starting registration flow")
	wac.Disconnect()
	inQrChan, _ := wac.GetQRChannel(context.Background())
	wac.Log.Debugf("Connecting to WhatsApp from qrCodeLoop() to start registration")
	err := wac.Connect()
	if err != nil {
		// we don't signal an error here because if it was a real connection
		// error we would have triggered it on the first connect above. chances
		// are we are re-using a websocket and running this function again will
		// yield a success
		//state.Errors <- err
		wac.Log.Warnf("qrCodeLoop error on second connect")
		return err, false
	}
	for {
		select {
		case evt := <-inQrChan:
			if evt.Event == "code" {
				state.QRCodes <- evt.Code
			} else if evt.Event == "success" {
				wac.Log.Debugf("Login event: %v", evt.Event)
				return nil, true
			} else {
				wac.Log.Debugf("Unknown event: %v", evt.Event)
				err := fmt.Errorf("Unknown event during login: %v: %s", evt.Code, evt.Event)
				state.Errors <- err
				return err, false
			}
		case <-ctx.Done():
			return nil, false
		case <-wac.ctxC.Done():
			return nil, false
		}
	}
}

func (wac *WhatsAppClient) GetMessages() *QueueClient {
	return wac.messageQueue.NewClient()
}

func (wac *WhatsAppClient) GetHistoryMessages() *QueueClient {
	return wac.historyMessageQueue.NewClient()
}

func (wac *WhatsAppClient) getMessages(evt interface{}) {
	wac.Log.Debugf("GetMessages handler got something: %T", evt)
	switch wmMsg := evt.(type) {
	case *events.Message:
		if wmMsg.Info.Category == "peer" {
			return
		}
		if !MessageHasContent(wmMsg) {
			return
		}

		wac.Log.Debugf("Setting newest message info: %s", wmMsg.Info.ID)
		wac.logNewestMessageInfo(&wmMsg.Info)

		wac.Log.Debugf("Checking ACL: %s", wmMsg.Info.ID)
		aclEntry, err := wac.aclStore.GetByJID(&wmMsg.Info.Chat)
		if err != nil {
			wac.Log.Errorf("Could not read ACL for JID: %s: %+v", wmMsg.Info.Chat.String(), err)
		}
		if !aclEntry.CanRead() {
			wac.Log.Debugf("Skipping message because we don't have read permissions in group")
			return
		}
		wac.Log.Debugf("Creating internal message type: %s", wmMsg.Info.ID)
		msg, err := NewMessageFromWhatsMeow(wac, wmMsg.UnwrapRaw())
		if err != nil {
			wac.Log.Errorf("Error converting message from whatsmeow: %+v", err)
			return
		}
		wac.Log.Debugf("Sending message to MessageQueue: %s: %s", wmMsg.Info.ID, msg.DebugString())
		wac.messageQueue.SendMessage(msg)
	}
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
			if *message.Data.SyncType == waProto.HistorySync_ON_DEMAND {
				if ctxWithCancel, found := wac.historyRequestContexts[chatJID.String()]; found {
					// stop retrying to get the history for this group
					ctxWithCancel.Cancel()
				}
			}

			aclEntry, err := wac.aclStore.GetByJID(&chatJID)
			if err != nil {
				wac.Log.Errorf("Could not read ACL for JID: %s: %+v", chatJID.String(), err)
				continue
			}

			canReadMessages := aclEntry.CanRead()
			if !canReadMessages {
				wac.Log.Debugf("Skipping history message because we don't have read permissions in group")
			}

			var oldestMsgInfo *types.MessageInfo
			var newestMsgInfo *types.MessageInfo
			for _, rawMsg := range conv.GetMessages() {
				wmMsg, err := wac.ParseWebMessage(chatJID, rawMsg.GetMessage())
				if err != nil {
					wac.Log.Errorf("Failed to parse raw history message: %v", err)
					continue
				}
				if !MessageHasContent(wmMsg) {
					continue
				}
				if oldestMsgInfo == nil || wmMsg.Info.Timestamp.Before(oldestMsgInfo.Timestamp) {
					oldestMsgInfo = &wmMsg.Info
				}
				if newestMsgInfo == nil || wmMsg.Info.Timestamp.After(newestMsgInfo.Timestamp) {
					newestMsgInfo = &wmMsg.Info
				}
				if canReadMessages {
					msg, err := NewMessageFromWhatsMeow(wac, wmMsg)
					if err != nil {
						wac.Log.Errorf("Failed to convert history message: %v", err)
						continue
					}
					wac.Log.Debugf("Sending message to HistoryMessageQueue")
					wac.historyMessageQueue.SendMessage(msg)
				}
			}
			if newestMsgInfo != nil {
				wac.logNewestMessageInfo(newestMsgInfo)
			}
			if *message.Data.SyncType == waProto.HistorySync_ON_DEMAND && oldestMsgInfo != nil {
				wac.Log.Infof("Continuing on demand history request")
				go wac.requestHistoryMsgInfo(oldestMsgInfo)
			}
		}
	}
}

func (wac *WhatsAppClient) RequestHistory(chat types.JID) error {
	if wac.encSQLStore == nil {
		wac.Log.Errorf("Tried to request history with a nil encSQLStore")
		return errors.New("EncSQLStore is nil, cannot find msg info")
	}
	msgInfo, err := wac.encSQLStore.GetNewestMessageInfo(chat)
	if err != nil {
		wac.Log.Errorf("Could not get newest chat message: %s: %+v", chat.String(), err)
		return err
	} else if msgInfo == nil {
		return ErrNoChatHistory
	}

	wac.requestHistoryMsgInfoRetry(msgInfo)
	return nil
}

func (wac *WhatsAppClient) requestHistoryMsgInfoRetry(msgInfo *types.MessageInfo) {
	attempts := 0
	key := msgInfo.Chat.String()
	ctxC, found := wac.historyRequestContexts[key]
	if found {
		ctxC.Cancel()
	}
	ctxC = NewContextWithCancel(wac.ctxC)
	wac.historyRequestContexts[key] = ctxC
	go func() {
		for {
			wac.requestHistoryMsgInfo(msgInfo)
			dt := ((1 << attempts) + 5) * time.Minute
			wac.Log.Infof("Waiting for history request. Will try again in: %s", dt)
			select {
			case <-time.After((1 << attempts) * time.Minute):
				attempts += 1
				if attempts > 11 {
					wac.Log.Warnf("Could not get group history after max number of attempts. Not retrying again: %s: %d", key, attempts)
					ctxC.Cancel()
					return
				}
				break
			case <-ctxC.Done():
				wac.Log.Infof("Got historical messages for group. Stopping retry loop: %s: %d", key, attempts)
				return
			}
		}
	}()
}

func (wac *WhatsAppClient) requestHistoryMsgInfo(msgInfo *types.MessageInfo) {
	if msgInfo == nil {
		return
	}
	wac.Log.Infof("Requesting history for group: %s", msgInfo.Chat.String())
	msg := wac.Client.BuildHistorySyncRequest(msgInfo, 50)
	// Context here should be bound to the whatsappclient's connection
	extras := whatsmeow.SendRequestExtra{Peer: true}
	ctx, _ := context.WithTimeout(wac.ctxC, time.Minute)
	wac.Client.SendMessage(ctx, wac.Client.Store.ID.ToNonAD(), msg, extras)
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
	lock := wac.mediaMutexMap.Lock(msgInfo.ID)
	defer lock.Unlock()

	data, err := wac.mediaCache.Get(msgInfo.ID)
	if data != nil {
		wac.Log.Debugf("Found cached version of image in DownloadAnyRetry: %v", msgInfo.ID)
		return data, nil
	}
	rateLimit(wac.mediaMutexMap, "download", 2*time.Second)

	wac.Log.Debugf("Downloading message: %v: %v", msg, msgInfo)
	data, err = wac.Client.DownloadAny(msg)
	if errors.Is(err, whatsmeow.ErrMediaDownloadFailedWith404) || errors.Is(err, whatsmeow.ErrMediaDownloadFailedWith410) || errors.Is(err, whatsmeow.ErrMediaDownloadFailedWith404) || errors.Is(err, whatsmeow.ErrMediaDownloadFailedWith403) {
		return wac.RetryDownload(ctx, msg, msgInfo)
	} else if err != nil {
		wac.Log.Errorf("Error trying to download message: %v", err)
	}
	if len(data) > 0 {
		wac.mediaCache.Add(msgInfo.ID, data)
	}
	return data, err
}

func (wac *WhatsAppClient) RetryDownload(ctx context.Context, msg *waProto.Message, msgInfo *types.MessageInfo) ([]byte, error) {
	lock := wac.mediaMutexMap.Lock(msgInfo.ID)
	defer lock.Unlock()

	data, err := wac.mediaCache.Get(msgInfo.ID)
	if data != nil {
		wac.Log.Debugf("Found cached version of image in RetryDownload: %v", msgInfo.ID)
		return data, nil
	}
	rateLimit(wac.mediaMutexMap, "download", 2*time.Second)

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
	err = wac.Client.SendMediaRetryReceipt(msgInfo, mediaKey)
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

	ctxTimeout, ctxCancel := context.WithTimeout(ctx, time.Minute)
	ctxRetry := ContextWithCancel{
		Context: ctxTimeout,
		cancel:  ctxCancel,
	}
	shouldRetryDownload := false
	evtHandler := wac.Client.AddEventHandler(func(evt interface{}) {
		switch retry := evt.(type) {
		case *events.MediaRetry:
			wac.Log.Infof("Got Media Retry for message download")
			if retry.MessageID == msgInfo.ID {
				retryData, err := whatsmeow.DecryptMediaRetryNotification(retry, mediaKey)
				if err != nil || retryData.GetResult() != waProto.MediaRetryNotification_SUCCESS {
					wac.Log.Errorf("Could not download media through a retry notification: %v: %s", err, retryData.GetResult().String())
					retryError = err
					ctxRetry.Cancel()
					return
				}
				// TODO: FIX: the following line may be the reason we are
				// getting 403's on historical media downloads
				wac.Log.Debugf("OLD direct path: %s", directPathValues[0].String())
				wac.Log.Debugf("NEW direct path: %s", *retryData.DirectPath)
				directPathValues[0].SetString(*retryData.DirectPath)
				shouldRetryDownload = true
				ctxRetry.Cancel()
			}
		}
	})
	defer wac.Client.RemoveEventHandler(evtHandler)

	wac.Log.Debugf("Waiting for retry download to complete")
	<-ctxRetry.Done()
	if shouldRetryDownload {
		body, retryError = wac.DownloadAny(msg)
		//body, retryError = wac.DownloadAnyRetry(ctxRetry.Context, msg, msgInfo)
	}
	if ctx.Err() != nil && retryError == nil {
		retryError = ErrDownloadRetryCanceled
	}
	if retryError != nil {
		wac.Log.Errorf("Error in retry handler: %v", retryError)
	}
	if len(body) > 0 {
		wac.Log.Debugf("Media Retry got body of length: %d", len(body))
		wac.mediaCache.Add(msgInfo.ID, body)
	}
	return body, retryError
}

func (wac *WhatsAppClient) logNewestMessageInfo(msgInfo *types.MessageInfo) {
	if msgInfo == nil {
		return
	}
	if wac.encSQLStore != nil {
		wac.Log.Debugf("Logging message info: %s: %s: %s", msgInfo.Timestamp.String(), msgInfo.Chat.String(), msgInfo.ID)
		err := wac.encSQLStore.PutNewestMessageInfo(msgInfo)
		if err != nil {
			wac.Log.Errorf("Could not insert message info: %+v", err)
		}
	}
}

func (wac *WhatsAppClient) GetGroupInfo(jid types.JID) (*types.GroupInfo, error) {
	chatJID := jid.ToNonAD().String()
	if groupInfo, ok := wac.groupInfoCache.Get(chatJID); ok {
		return groupInfo, nil
	}
	groupInfo, err := wac.Client.GetGroupInfo(jid)
	if err == nil {
		wac.groupInfoCache.Add(chatJID, groupInfo)
	}
	return groupInfo, err
}
