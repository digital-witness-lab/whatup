package whatupcore2

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var version = "0.0.1"

var rootCmd = &cobra.Command{
	Use:     "whatupcore2",
	Version: version,
	Short:   "whatupcore2 - whatupcore cli tool and service",
	Long: `whatupcore2 controls whatup's connection to WhatsApp and the storage of credentials
   
    Use this CLI tool to run the whatupcore2 service and interact with the
    various tools it provides to simplify the maintenance of the whatup system`,
	Run: func(cmd *cobra.Command, args []string) {

	},
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Whoops. There was an error while executing your CLI '%s'", err)
		os.Exit(1)
	}
}
