package whatupcore2

import (
	"context"
	"errors"
	"fmt"
	"time"
)

var (
	SessionTimeout = 10 * time.Minute // TODO: this should probably be the same as the JWT timeout?
)

type SessionManager struct {
	idToSession map[string]*Session
	secretKey   []byte

	cancelFunc context.CancelFunc
}

func NewSessionManager(secretKey []byte) *SessionManager {
	return &SessionManager{
		idToSession: make(map[string]*Session),
		secretKey:   secretKey,
	}
}

func (sm *SessionManager) Start() {
	ctx, cancel := context.WithCancel(context.Background())
	sm.cancelFunc = cancel

	go func(ctx context.Context) {
		ticker := time.NewTicker(SessionTimeout)
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
	oldest := time.Now().Add(-SessionTimeout)
	nRemoved := 0
	for _, session := range sm.idToSession {
		if oldest.Compare(session.lastAccess) > 0 {
			sm.removeSession(session)
			nRemoved += 1
		}
	}
	if nRemoved > 0 {
		fmt.Printf("Pruned sessions: %d sessions removed\n", nRemoved)
	}
}

func (sm *SessionManager) AddLogin(username string, passphrase string) (*Session, error) {
	session, err := NewSessionLogin(username, passphrase, sm.secretKey)
	if err != nil {
		return nil, err
	}

	sm.addSession(session)
	return session, nil
}

func (sm *SessionManager) AddRegistration(ctx context.Context, username string, passphrase string) (*Session, *RegistrationState, error) {
	session, state, err := NewSessionRegister(ctx, username, passphrase, sm.secretKey)
	if err != nil {
		return nil, nil, err
	}

	if err := sm.addSession(session); err != nil {
		return nil, nil, err
	}
	go func(session *Session, state *RegistrationState) {
		state.Wait()
		if !state.Success {
			session.Client.Log.Errorf("Registration session done and not successful. Removing from SessionManager")
			sm.removeSession(session)
		}
	}(session, state)
	return session, state, nil
}

func (sm *SessionManager) addSession(session *Session) error {
	if _, collision := sm.idToSession[session.sessionId]; collision {
		return errors.New("Session ID Collision in SessionManager. Panic.")
	}

	sm.idToSession[session.sessionId] = session
	// TODO: add timer to remove stale idToSession (token expiration?)
	return nil
}

func (sm *SessionManager) removeSession(session *Session) bool {
	if _, sessionExists := sm.idToSession[session.sessionId]; !sessionExists {
		return false
	}
	session.Close()
	delete(sm.idToSession, session.sessionId)
	return true
}

func (sm *SessionManager) TokenToSessionId(token string) (string, error) {
	return parseTokenString(token, sm.secretKey)
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
	session, found := sm.idToSession[sessionId]
	if !found {
		return nil, false
	}
	session.lastAccess = time.Now()
	return session, found
}
