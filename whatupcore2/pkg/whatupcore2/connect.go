package whatupcore2

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/mdp/qrterminal/v3"

	waLog "go.mau.fi/whatsmeow/util/log"

	_ "github.com/mattn/go-sqlite3"
)

func WhatsAppServe(username string, passphrase string) error {
    log := waLog.Stdout("WhatsAppServe", "DEBUG", true)
    client, error := NewWhatsAppClient(username, passphrase)
    if error != nil {
        return error
    }

    signalChan := make(chan os.Signal, 1)
    signal.Notify(signalChan, os.Interrupt, syscall.SIGTERM)
    defer close(signalChan)

    ctx := context.Background()
    ctx, cancel := context.WithCancel(ctx)
    regState := client.LoginOrRegister(ctx)
    defer client.Disconnect()
    for !regState.Completed {
        select {
        case qrCode, open := <- regState.QRCodes:
            if !open {
                break
            }
            fmt.Println(qrCode)
            qrterminal.GenerateHalfBlock(qrCode, qrterminal.L, os.Stdout)
        case err, open := <- regState.Errors:
            if !open {
                break
            }
            fmt.Printf("Recieved error while logging in: %+v\n", err)
            return err
        case <- signalChan:
            log.Infof("Got system signal chan message")
            cancel()
            return nil
        case <- ctx.Done():
            log.Infof("WhatsAppServe login context marked done")
            return context.Cause(ctx)
        }
    }

    log.Infof("!!!!Login or Registration done. Serving until interrupt")
    <- signalChan
    return nil
}
