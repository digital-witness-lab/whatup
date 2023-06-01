package whatupcore2

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"

	"github.com/mdp/qrterminal/v3"

	"go.mau.fi/whatsmeow"
	"go.mau.fi/whatsmeow/store/sqlstore"
	"go.mau.fi/whatsmeow/types/events"
	waLog "go.mau.fi/whatsmeow/util/log"

	_ "github.com/mattn/go-sqlite3"
)

const (
    DB_ROOT = "db"
)

func eventHandler(evt interface{}) {
    switch v := evt.(type) {
    case *events.Message:
        fmt.Println("Received a message!", v.Message.GetConversation())
    }
}

func hashStringHex(unhashed string) string {
    h := sha256.New()
    h.Write([]byte(unhashed))
    hash := hex.EncodeToString(h.Sum(nil))
    return hash
}

func createDBFilePath(username string, n_subdirs int) (string, error) {
    if (n_subdirs < 1) {
        return "", fmt.Errorf("n_subdirs must be >= 1: %d", n_subdirs)
    }
    path_username := filepath.Join(strings.Split(username[0:n_subdirs], "")...)
    path := filepath.Join(".", DB_ROOT, path_username)
    err := os.MkdirAll(path, 0700)
    if (err != nil) {
        return "", err
    }
    return filepath.Join(path, fmt.Sprintf("%s.db", username)), nil
}

func cleanupDBFile(path string) {
    for path != DB_ROOT && path != "."{
        err := os.Remove(path)
        if (err != nil) {
            return
        }
        path = filepath.Dir(path)
    }
}

func WhatsAppConnect(username string, passphrase string) error {
    dbLog := waLog.Stdout("Database", "DEBUG", true)

    username_safe := hashStringHex(username)
    passphrase_safe := hashStringHex(passphrase)
    db_path, err := createDBFilePath(username_safe, 4)
    if err != nil {
        return err
    }
    fmt.Println("Using database file:", db_path)
    db_uri := fmt.Sprintf("file:%s?_foreign_keys=on&_key=%s", db_path, passphrase_safe)
    container, err := sqlstore.New("sqlite3", db_uri, dbLog)
    if err != nil {
        return err
    }
    deviceStore, err := container.GetFirstDevice()
    if err != nil {
        return err
    }
    clientLog := waLog.Stdout("Client", "DEBUG", true)
    client := whatsmeow.NewClient(deviceStore, clientLog)
    client.AddEventHandler(eventHandler)

    signalChan := make(chan os.Signal, 1)
    signal.Notify(signalChan, os.Interrupt, syscall.SIGTERM)

    if client.Store.ID == nil {
        // No ID stored, new login
        loggedin := false
        defer func() {
            if (!loggedin) {
                fmt.Println("No login detected... deleteing temporary DB file:", db_path)
                cleanupDBFile(db_path)
            }
        }()
        qrChan, _ := client.GetQRChannel(context.Background())
        err = client.Connect()
        if err != nil {
            return err
        }
        defer client.Disconnect()

        for {
            select {
            case evt := <- qrChan:
                if evt.Event == "code" {
                    fmt.Println("QR code:")
                    qrterminal.GenerateHalfBlock(evt.Code, qrterminal.L, os.Stdout)
                } else {
                    loggedin = true
                    fmt.Println("Login event:", evt.Event)
                }
            case <- signalChan:
                return nil
            }
        }
    } else {
        // Already logged in, just connect
        err = client.Connect()
        if err != nil {
            return err
        }
        defer client.Disconnect()
    }

    fmt.Println("Waiting for interrupt")
    <-signalChan
    fmt.Println("Cleanly exiting")
    return nil
}
