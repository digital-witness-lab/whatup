package whatupcore2

import (
	"context"
	"errors"
)

type SessionManager struct {
    tokenToSession map[string]*Session
    secretKey []byte
}

func NewSessionManager(secretKey []byte) (*SessionManager, error) {
    return &SessionManager{
        tokenToSession: make(map[string]*Session),
        secretKey: secretKey,
    }, nil
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
        if ! state.Success {
            session.Client.Log.Errorf("Registration session done and not successful. Removing from SessionManager")
            sm.removeSession(session)
        }
    }(session, state)
    return session, state, nil
}

func (sm *SessionManager) addSession(session *Session) error {
    if _, collision := sm.tokenToSession[session.tokenString]; collision {
        return errors.New("Token Collision in SessionManager. Panic.")
    }

    sm.tokenToSession[session.tokenString] = session
    // TODO: add timer to remove stale tokenToSession (token expiration?)
    return nil
}

func (sm *SessionManager) removeSession(session *Session) bool {
    if _, sessionExists := sm.tokenToSession[session.tokenString]; !sessionExists {
        return false
    }
    delete(sm.tokenToSession, session.tokenString)
    return true
}

func (sm *SessionManager) RenewSessionToken(token string) (*Session, error) {
    session, found := sm.tokenToSession[token]
    if !found {
        return nil, errors.New("Could not find session")
    }
    return session, session.RenewToken(sm.secretKey)
}

func (sm *SessionManager) GetSession(token string) (*Session, bool) {
    session, found := sm.tokenToSession[token]
    return session, found
}
