package whatupcore2

import (
	"fmt"
	"os"
	"syscall"

	"golang.org/x/term"

	"github.com/digital-witness-lab/whatup/whatupcore2/pkg/whatupcore2"
	"github.com/spf13/cobra"
)

func readPassphraseStdin() string {
	fmt.Print("Passphrase> ")
	passphrase_bytes, err := term.ReadPassword(int(syscall.Stdin))
	if err != nil {
		panic(err)
	}
	passphrase := string(passphrase_bytes)
	return passphrase
}

var whatsUpConnectCmd = &cobra.Command{
	Use:     "connect [username] [passphrase]",
	Aliases: []string{"c"},
	Short:   "Connects to WhatsApp and maintains a connection",
	Long: `Connect to WhatsApp using a given username and passphrase and
    maintains the connection. This connection can be interacted with the
    gRPC interface.

    If passphrase is set to - then we read the passphrase from STDIN. If
    passphrase is set to ENV then we read the passphrase from the envvar
    WHATUPCORE2_PASSPHRASE
    `,
	Args: cobra.ExactArgs(2),
	Run: func(cmd *cobra.Command, args []string) {
		username := args[0]
		passphrase := args[1]

		if passphrase == "-" {
			passphrase = readPassphraseStdin()
		} else if passphrase == "ENV" {
			var ok bool
			passphrase, ok = os.LookupEnv("WHATUPCORE2_PASSPHRASE")
			if !ok {
				panic("Passphrase set to envvar WHATUPCORE2_PASSPHRASE, but no such envvar found")
			}
		}
		if len(passphrase) == 0 {
			panic("passphrase is empty")
		}
		if len(username) == 0 {
			panic("username is empty")
		}

		fmt.Println("Connecting to WhatsApp")
		err := whatupcore2.WhatsAppServe(username, passphrase)
		if err != nil {
			fmt.Println("Error:", err)
			panic(err)
		}
		fmt.Println("Goodbye")
	},
}

func init() {
	// TODO: have DB path be a config variable / flag
	rootCmd.AddCommand(whatsUpConnectCmd)
}
