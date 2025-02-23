package whatupcore2

import (
	"context"
	"errors"
	"time"

	pb "github.com/digital-witness-lab/whatup/protos"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

const (
	SessionExpirationTick = 10 * time.Minute
)

var (
	ErrSessionManagerInvalidState = status.Error(codes.Internal, "Invalid SessionManager state")
	ErrInvalidPassphrase          = status.Error(codes.Unauthenticated, "Could not authenticate")
)

type SessionManager struct {
	sessionIdToSession  map[string]*Session
	usernameToSessionId map[string]string
	secretKey           []byte
	dbUri               string

	log         waLog.Logger
	sessionLock *MutexMap

	ctxC ContextWithCancel
}

func NewSessionManager(secretKey []byte, dbUri string, log waLog.Logger) *SessionManager {
	return &SessionManager{
		sessionIdToSession:  make(map[string]*Session),
		usernameToSessionId: make(map[string]string),
		secretKey:           secretKey,
		dbUri:               dbUri,
		log:                 log,
		sessionLock:         NewMutexMap(log.Sub("LOCK")),
	}
}

func (sm *SessionManager) Start() {
	ctxC := NewContextWithCancel(context.Background())
	sm.ctxC = ctxC

	go func(ctx context.Context) {
		ticker := time.NewTicker(SessionExpirationTick)
		for {
			select {
			case <-ticker.C:
				sm.pruneSessions()
			case <-ctxC.Done():
				return
			}
		}
	}(ctxC)
}

func (sm *SessionManager) Stop() {
	if !sm.ctxC.IsZero() {
		sm.ctxC.Cancel()
	}
}

func (sm *SessionManager) pruneSessions() {
	nRemoved := 0
	for _, session := range sm.sessionIdToSession {
		if session.IsExpired() {
			sm.log.Debugf("Removing old session: %v", session.lastAccess)
			sm.removeSession(session)
			nRemoved += 1
		}
	}
	if nRemoved > 0 {
		sm.log.Infof("Pruned sessions: %d sessions removed\n", nRemoved)
	}
}

func (sm *SessionManager) AddLogin(username string, passphrase string) (*Session, error) {
	lock := sm.sessionLock.Lock(username)
	defer lock.Unlock()

	session, err := sm.GetSessionLogin(username, passphrase)
	if err != nil {
		return nil, err
	} else if session != nil {
		return session, nil
	}

	session, err = NewSessionLogin(username, passphrase, sm.secretKey, sm.dbUri, sm.log.Sub(username))
	if err != nil {
		return nil, err
	}

	session.log.Infof("New Login Session Created")
	sm.addSession(session)
	return session, nil
}

func (sm *SessionManager) AddRegistration(ctx context.Context, username string, passphrase string, registerOptions *pb.RegisterOptions) (*Session, *RegistrationState, error) {
	lock := sm.sessionLock.Lock(username)
	defer lock.Unlock()

	session, err := sm.GetSessionLogin(username, passphrase)
	if err != nil {
		return nil, nil, err
	} else if session != nil {
		return session, nil, nil
	}

	session, state, err := NewSessionRegister(ctx, username, passphrase, registerOptions, sm.secretKey, sm.dbUri, sm.log.Sub(username))
	if err != nil || state == nil {
		return nil, nil, err
	}
	if err := sm.addSession(session); err != nil {
		return nil, nil, err
	}

	go func(session *Session, state *RegistrationState) {
		state.Wait()
		if !state.Success {
			session.log.Errorf("Registration session done and not successful. Removing from SessionManager")
			sm.removeSession(session)
		}
	}(session, state)
	session.log.Infof("New Register Session Created")
	return session, state, nil
}

func (sm *SessionManager) addSession(session *Session) error {
	if _, collision := sm.sessionIdToSession[session.sessionId]; collision {
		return errors.New("Session ID Collision in SessionManager. Panic.")
	}

	sm.sessionIdToSession[session.sessionId] = session
	sm.usernameToSessionId[session.Username] = session.sessionId
	return nil
}

func (sm *SessionManager) removeSession(session *Session) bool {
	if _, sessionExists := sm.sessionIdToSession[session.sessionId]; !sessionExists {
		return false
	}
	sm.log.Debugf("Removing session: %s: %s", session.Username, session.sessionId)
	session.Close()
	delete(sm.sessionIdToSession, session.sessionId)
	delete(sm.usernameToSessionId, session.Username)
	return true
}

func (sm *SessionManager) TokenToSessionId(token string) (string, error) {
	claims, err := parseTokenString(token, sm.secretKey)
	if err != nil {
		return "", err
	}
	return claims.SessionId, nil
}

func (sm *SessionManager) RenewSessionToken(sessionId string) (*Session, error) {
	session, found := sm.GetSession(sessionId)
	if !found {
		return nil, errors.New("Could not find session")
	}
	err := session.RenewToken(sm.secretKey)
	return session, err
}

func (sm *SessionManager) GetSession(sessionId string) (*Session, bool) {
	session, found := sm.sessionIdToSession[sessionId]
	if !found {
		return nil, false
	}
	session.UpdateLastAccess()
	return session, found
}

func (sm *SessionManager) GetSessionLogin(username, passphrase string) (*Session, error) {
	sessionId, found := sm.usernameToSessionId[username]
	if !found {
		return nil, nil
	}
	session, found := sm.GetSession(sessionId)
	if !found {
		sm.log.Errorf("Invalid SessionManager state... username found with no corresponding sessionID")
		return nil, ErrSessionManagerInvalidState
	}
	if !session.VerifyPassphrase(passphrase) {
		sm.log.Warnf("Invalid login attempt for user: %s", username)
		return nil, ErrInvalidPassphrase
	}
	if session.Client.IsClosed() || !session.Client.IsLoggedIn() {
		sm.log.Warnf("Trying to log into a disconnected client!")
		sm.removeSession(session)
		return nil, nil
	}
	session.log.Infof("User logged in to existing session")
	return session, nil
}

func (sm *SessionManager) Close() {
	sm.log.Infof("Closing session manager")
	sm.ctxC.Cancel()
	for _, session := range sm.sessionIdToSession {
		sm.removeSession(session)
	}
}
