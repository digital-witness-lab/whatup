package whatupcore2

import (
	"fmt"

	"github.com/digital-witness-lab/whatup/whatupcore2/pkg/whatupcore2"
	"github.com/spf13/cobra"
)

var onlyDigits bool
var inspectCmd = &cobra.Command{
    Use:   "inspect",
    Aliases: []string{"insp"},
    Short:  "Inspects a string",
    Args:  cobra.ExactArgs(1),
    Run: func(cmd *cobra.Command, args []string) {

        i := args[0]
        res, kind := whatupcore2.Inspect(i, onlyDigits)

        pluralS := "s"
        if res == 1 {
            pluralS = ""
        }
        fmt.Printf("'%s' has %d %s%s.\n", i, res, kind, pluralS)
    },
}

func init() {
    inspectCmd.Flags().BoolVarP(&onlyDigits, "digits", "d", false, "Count only digits")
    rootCmd.AddCommand(inspectCmd)
}
