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

	log waLog.Logger

	cancelFunc context.CancelFunc
}

func NewSessionManager(secretKey []byte, log waLog.Logger) *SessionManager {
	return &SessionManager{
		sessionIdToSession:  make(map[string]*Session),
		usernameToSessionId: make(map[string]string),
		secretKey:           secretKey,
		log:                 log,
	}
}

func (sm *SessionManager) Start() {
	ctx, cancel := context.WithCancel(context.Background())
	sm.cancelFunc = cancel

	go func(ctx context.Context) {
		ticker := time.NewTicker(SessionExpirationTick)
		for {
			select {
			case <-ticker.C:
				sm.pruneSessions()
			case <-ctx.Done():
				return
			}
		}
	}(ctx)
}

func (sm *SessionManager) Stop() {
	if sm.cancelFunc != nil {
		sm.cancelFunc()
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
	session, err := sm.GetSessionLogin(username, passphrase)
	if err != nil {
		return nil, err
	} else if session != nil {
		return session, nil
	}

	session, err = NewSessionLogin(username, passphrase, sm.secretKey, sm.log.Sub(username))
	if err != nil {
		return nil, err
	}

	session.log.Infof("New Login Session Created")
	sm.addSession(session)
	return session, nil
}

func (sm *SessionManager) AddRegistration(ctx context.Context, username string, passphrase string, registerOptions *pb.RegisterOptions) (*Session, *RegistrationState, error) {
	session, err := sm.GetSessionLogin(username, passphrase)
	if err != nil {
		return nil, nil, err
	} else if session != nil {
		return session, nil, nil
	}

	session, state, err := NewSessionRegister(ctx, username, passphrase, registerOptions, sm.secretKey, sm.log.Sub(username))
	if err != nil {
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
	session.log.Infof("User logged in to existing session")
	return session, nil
}
