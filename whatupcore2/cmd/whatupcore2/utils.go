package whatupcore2

import (
	"fmt"
	"os"
	"strings"
)

func MustGetEnv(key string) string {
	value, ok := os.LookupEnv(key)
	if !ok {
		panic(fmt.Errorf("Could not find envvar %s", key))
	}
	return value
}

func getPhotoCopUriFromEnv() string {
	if photoCopUri, ok := os.LookupEnv("PHOTOCOP_URI"); ok {
		return photoCopUri
	}
	return ""
}

func getDbUriFromEnv() string {
	if dbUri, ok := os.LookupEnv("DATABASE_URL"); ok {
		return dbUri
	}
	var (
		host         = "db"
		username     = MustGetEnv("POSTGRES_DATABASE")
		passwordFile = MustGetEnv("POSTGRES_PASSWORD_FILE")
		database     = MustGetEnv("POSTGRES_DATABASE")
	)
	passwordBytes, err := os.ReadFile(passwordFile)
	if err != nil {
		panic(err)
	}
	passwordStr := strings.TrimSpace(string(passwordBytes))
	return fmt.Sprintf("postgresql://%s:%s@%s/%s?sslmode=disable", username, passwordStr, host, database)
}
