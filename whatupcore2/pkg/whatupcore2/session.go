package whatupcore2

import (
	"context"
	"time"

	"github.com/alexedwards/argon2id"
	pb "github.com/digital-witness-lab/whatup/protos"
	jwt "github.com/golang-jwt/jwt/v5"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/protobuf/types/known/timestamppb"
)

type Session struct {
	Username       string
	passphraseHash string
	sessionId      string
	token          *jwt.Token
	tokenString    string

	ctxC ContextWithCancel

	createdAt  time.Time
	renewedAt  time.Time
	lastAccess time.Time

	log    waLog.Logger
	Client *WhatsAppClient
}

func NewSessionDisconnected(username, passphrase string, secretKey []byte, log waLog.Logger) (*Session, error) {
	now := time.Now()

	hash, err := argon2id.CreateHash(passphrase, argon2id.DefaultParams)
	if err != nil {
		panic(err)
	}

	ctxC := NewContextWithCancel(context.Background())

	session := &Session{
		Username:       username,
		passphraseHash: hash,
		sessionId:      username,
		ctxC:           ctxC,
		createdAt:      now,
		renewedAt:      now,
		lastAccess:     now,
		log:            log,
	}
	session.RenewToken(secretKey)
	return session, nil
}

func NewSessionLogin(username string, passphrase string, secretKey []byte, dbUri string, log waLog.Logger) (*Session, error) {
	session, err := NewSessionDisconnected(username, passphrase, secretKey, log.Sub(username))
	if err != nil {
		return nil, err
	}

	if err = session.Login(username, passphrase, dbUri); err != nil {
		log.Errorf("Could not login... closing session: %+v", err)
		return nil, err
	}
	return session, nil
}

func NewSessionRegister(ctx context.Context, username string, passphrase string, registerOptions *pb.RegisterOptions, secretKey []byte, dbUri string, log waLog.Logger) (*Session, *RegistrationState, error) {
	session, err := NewSessionDisconnected(username, passphrase, secretKey, log)
	if err != nil {
		return nil, nil, err
	}

	state, err := session.LoginOrRegister(ctx, username, passphrase, registerOptions, dbUri)
	if err != nil {
		return nil, nil, err
	}
	return session, state, nil
}

func (session *Session) Close() {
	session.log.Debugf("Closing session")
	session.ctxC.Cancel()
	session.Client.Close()
}

func (session *Session) ToProto() *pb.SessionToken {
	expirationTime, _ := session.GetExpirationTime()
	return &pb.SessionToken{Token: session.TokenString(), ExpirationTime: timestamppb.New(expirationTime)}
}

func (session *Session) Login(username string, passphrase string, dbUri string) error {
	session.log.Infof("Creating new login for user: %s", username)
	client, err := NewWhatsAppClient(session.ctxC, username, passphrase, dbUri, false, session.log.Sub("WAC"))
	if err != nil {
		client.Close()
		return err
	}

	if err := client.Login(2 * time.Minute); err != nil {
		client.Close()
		return err
	}
	session.Client = client
	return nil
}

func (session *Session) LoginOrRegister(ctx context.Context, username string, passphrase string, registerOptions *pb.RegisterOptions, dbUri string) (*RegistrationState, error) {
	client, err := NewWhatsAppClient(session.ctxC, username, passphrase, dbUri, registerOptions.GetHistory, session.log.Sub("WAC"))
	if err != nil {
		return nil, err
	}

	state := client.LoginOrRegister(ctx, registerOptions)
	session.Client = client
	return state, nil
}

func (session *Session) RenewToken(secretKey []byte) error {
	token := createJWTToken(session.Username, session.sessionId)
	tokenString, err := token.SignedString(secretKey)
	if err != nil {
		return err
	}

	session.renewedAt = time.Now()
	session.token = token
	session.tokenString = tokenString
	return nil
}

func (session *Session) GetExpirationTime() (time.Time, bool) {
	exp, err := session.token.Claims.GetExpirationTime()
	if err != nil {
		return time.Time{}, false
	}
	return exp.Time, true
}

func (session *Session) IsExpired() bool {
	exp, ok := session.GetExpirationTime()
	if !ok {
		return false
	}
	return exp.Before(time.Now())
}

func (session *Session) TokenString() string {
	return session.tokenString
}

func (session *Session) VerifyPassphrase(passphrase string) bool {
	match, _ := argon2id.ComparePasswordAndHash(passphrase, session.passphraseHash)
	return match
}

func (session *Session) UpdateLastAccess() {
	session.lastAccess = time.Now()
}

func (session *Session) UpdateLastAccessWhileAlive(ctx context.Context) {
	session.log.Debugf("Starting session last-access refresher")
	ticker := time.NewTicker(time.Minute)
	for {
		session.UpdateLastAccess()
		select {
		case <-ticker.C:
			continue
		case <-ctx.Done():
			session.log.Debugf("Stopping last-access refresher")
			return
		case <-session.ctxC.Done():
			session.log.Debugf("Session closed")
			return
		case <-session.Client.Done():
			session.log.Debugf("Client disconnected")
			session.Close()
			return
		}
	}
}

func (session *Session) IsLastAccessBefore(t time.Time) bool {
	return session.lastAccess.Compare(t) < 0
}
