package whatupcore2

import (
	"context"
	"time"

	pb "github.com/digital-witness-lab/whatup/protos"
	jwt "github.com/golang-jwt/jwt/v5"
)

type Session struct {
    Username string
    token *jwt.Token
    tokenString string

    createdAt time.Time
    renewedAt time.Time

    Client *WhatsAppClient
}

func NewSessionDisconnected(username string, secretKey []byte) (*Session, error) {
    session := &Session{
        Username: username,
        createdAt: time.Now(),
    }
    session.RenewToken(secretKey)
    return session, nil
}

func NewSessionLogin(username string, passphrase string, secretKey []byte) (*Session, error) {
    session, err := NewSessionDisconnected(username, secretKey)
    if err != nil {
        return nil, err
    }

    if err = session.Login(username, passphrase); err != nil {
        return nil, err
    }
    return session, nil
}

func NewSessionRegister(ctx context.Context, username string, passphrase string, secretKey []byte) (*Session, *RegistrationState, error) {
    session, err := NewSessionDisconnected(username, secretKey)
    if err != nil {
        return nil, nil, err
    }

    state, err := session.LoginOrRegister(ctx, username, passphrase)
    if err != nil {
        return nil, nil, err
    }
    return session, state, nil
}

func (session *Session) ToProto() *pb.SessionToken {
    return &pb.SessionToken{Token: session.TokenString()}
}


func (session *Session) Login(username string, passphrase string) error {
    client, err := NewWhatsAppClient(username, passphrase)
    if err != nil {
        return err
    }

    if err := client.Login(5 * time.Second); err != nil {
        return err
    }
    session.Client = client 
    return nil
}

func (session *Session) LoginOrRegister(ctx context.Context, username string, passphrase string) (*RegistrationState, error) {
    client, err := NewWhatsAppClient(username, passphrase)
    if err != nil {
        return nil, err
    }

    state := client.LoginOrRegister(ctx)
    session.Client = client 
    return state, nil
}

func (session *Session) RenewToken(secretKey []byte) error {
    token:= createJWTToken(session.Username, randomToken())
    tokenString, err := token.SignedString(secretKey)
    if err != nil {
        return err
    }

    session.renewedAt = time.Now()
    session.token = token
    session.tokenString = tokenString
    return nil
}

func (session *Session) IsExpired() bool {
    exp, err := session.token.Claims.GetExpirationTime()
    if err != nil {
        return true
    }
    return exp.Before(time.Now())
}

func (session *Session) TokenString() string {
    return session.tokenString
}

