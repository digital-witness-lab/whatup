package whatupcore2

import (
	"crypto/rand"
	"encoding/hex"
	"errors"
	"fmt"
	"time"

	jwt "github.com/golang-jwt/jwt/v5"
)

var (
	ErrInvalidToken    = errors.New("Invalid Token")
	ErrUnparsableClaim = errors.New("Token Invalid: Unparsable claims")
)

const (
	TOKEN_EXPIRATION  = 7 * 24 * time.Hour
	TOKEN_VERSION     = "whatupcore2.v0.1"
	TOKEN_LENGTH      = 64
	EXPIRATION_LEEWAY = 30 * time.Second
)

type SessionJWTClaims struct {
	Username  string `json:"username"`
	SessionId string `json:"token"`
	jwt.RegisteredClaims
}

func (claims SessionJWTClaims) Validate() error {
	if claims.Issuer != TOKEN_VERSION {
		return jwt.ErrTokenInvalidIssuer
	}
	return nil
}

func randomString() string {
	b := make([]byte, TOKEN_LENGTH)
	if _, err := rand.Read(b); err != nil {
		return ""
	}
	return hex.EncodeToString(b)
}

func createJWTToken(username string, sessionId string) *jwt.Token {
	claims := SessionJWTClaims{
		username,
		sessionId,
		jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(TOKEN_EXPIRATION)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			NotBefore: jwt.NewNumericDate(time.Now()),
			Issuer:    TOKEN_VERSION,
		},
	}

	tokenObj := jwt.NewWithClaims(jwt.SigningMethodHS512, claims)
	return tokenObj
}

func parseTokenString(tokenString string, secret []byte) (*SessionJWTClaims, error) {
	token, err := jwt.ParseWithClaims(
		tokenString,
		&SessionJWTClaims{},
		func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("Unexpected signing method: %v", token.Header["alg"])
			}
			return secret, nil
		},
		jwt.WithLeeway(EXPIRATION_LEEWAY),
	)
	if err != nil {
		return nil, err
	}
	if !token.Valid {
		return nil, ErrInvalidToken
	}

	claims, ok := token.Claims.(*SessionJWTClaims)
	if !ok {
		return nil, ErrUnparsableClaim
	}

	return claims, nil
}
