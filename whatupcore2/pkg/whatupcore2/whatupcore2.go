package whatupcore2

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/mdp/qrterminal/v3"

	"go.mau.fi/whatsmeow"
	"go.mau.fi/whatsmeow/store/sqlstore"
	"go.mau.fi/whatsmeow/types/events"
	waLog "go.mau.fi/whatsmeow/util/log"

	_ "github.com/mattn/go-sqlite3"
)

func eventHandler(evt interface{}) {
    switch v := evt.(type) {
    case *events.Message:
        fmt.Println("Received a message!", v.Message.GetConversation())
    }
}

func WhatsAppConnect() {
    dbLog := waLog.Stdout("Database", "DEBUG", true)
    // Make sure you add appropriate DB connector imports, e.g.
    // github.com/mattn/go-sqlite3 for SQLite
    container, err := sqlstore.New("sqlite3", "file:whatupcore2.db?_foreign_keys=on", dbLog)
    if err != nil {
        panic(err)
    }
    // If you want multiple sessions, remember their JIDs and use
    // .GetDevice(jid) or .GetAllDevices() instead.
    deviceStore, err := container.GetFirstDevice()
    if err != nil {
        panic(err)
    }
    clientLog := waLog.Stdout("Client", "DEBUG", true)
    client := whatsmeow.NewClient(deviceStore, clientLog)
    client.AddEventHandler(eventHandler)

    if client.Store.ID == nil {
        // No ID stored, new login
        qrChan, _ := client.GetQRChannel(context.Background())
        err = client.Connect()
        if err != nil {
            panic(err)
        }
        for evt := range qrChan {
            if evt.Event == "code" {
                // Render the QR code here e.g.
                // qrterminal.GenerateHalfBlock(evt.Code, qrterminal.L,
                // os.Stdout) or just manually `echo 2@... | qrencode -t
                // ansiutf8` in a terminal
                fmt.Println("QR code:")
                qrterminal.GenerateHalfBlock(evt.Code, qrterminal.L, os.Stdout)
            } else {
                fmt.Println("Login event:", evt.Event)
            }
        }
    } else {
        // Already logged in, just connect
        err = client.Connect()
        if err != nil {
            panic(err)
        }
    }

    // Listen to Ctrl+C (you can also do something else that prevents the program from exiting)
    c := make(chan os.Signal)
    signal.Notify(c, os.Interrupt, syscall.SIGTERM)
    <-c

    client.Disconnect()
}
