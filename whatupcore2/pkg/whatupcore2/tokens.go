package whatupcore2

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"time"

	jwt "github.com/golang-jwt/jwt/v5"
)

var (
    TOKEN_EXPIRATION = 7 * 24 * time.Hour
    TOKEN_VERSION = "whatupcore2.v0.1"
    TOKEN_LENGTH = 64
    EXPIRATION_LEEWAY = 30 * time.Second
)


type SessionJWTClaims struct {
	Username string `json:"username"`
	Token string `json:"token"`
	jwt.StandardClaims
}


func randomToken() string {
    b := make([]byte, TOKEN_LENGTH)
    if _, err := rand.Read(b); err != nil {
        return ""
    }
    return hex.EncodeToString(b)
}


func createJWTToken(username string, token string) *jwt.Token {
    claims := SessionJWTClaims{
        username,
        token,
        jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(TOKEN_EXPIRATION)),
		    IssuedAt:  jwt.NewNumericDate(time.Now()),
		    NotBefore: jwt.NewNumericDate(time.Now()),
            Issuer: TOKEN_VERSION,
        },
    }

    tokenObj := jwt.NewWithClaims(jwt.SigningMethodHS512, claims)
    return tokenObj
}

func verifyTokenString(tokenString string, secret []byte) (bool, error) {
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
        return false, err
    }
    if !token.Valid {
        return false, fmt.Errorf("Token Invalid")
    }

    claims, ok := token.Claims.(*SessionJWTClaims)
    if !ok {
        return false, fmt.Errorf("Token Invalid: Unparsable claims")
    }

    return true, nil
}
