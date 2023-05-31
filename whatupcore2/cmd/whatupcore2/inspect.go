package whatupcore2

import (
	"fmt"

	"github.com/digital-witness-lab/whatup/whatupcore2/pkg/whatupcore2"
	"github.com/spf13/cobra"
)

var onlyDigits bool
var whatsAppConnectCmd = &cobra.Command{
    Use:   "connect",
    Aliases: []string{"insp"},
    Short:  "Connects to WhatsApp and maintains a connection",
    Args:  cobra.ExactArgs(0),
    Run: func(cmd *cobra.Command, args []string) {

        fmt.Println("Connecting to WhatsApp")
        whatupcore2.WhatsAppConnect()
    },
}

func init() {
    rootCmd.AddCommand(whatsAppConnectCmd)
}
