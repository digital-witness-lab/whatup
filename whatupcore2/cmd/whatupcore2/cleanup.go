package whatupcore2

import (
	"fmt"
	"os"

	"github.com/digital-witness-lab/whatup/whatupcore2/pkg/whatupcore2"
	"github.com/spf13/cobra"
)

var (
	whatsUpRemoveUserCmd = &cobra.Command{
		Aliases: []string{"r"},
		Use:     "remove-user [username]",
		Short:   "Removes session data for user",
		Args:    cobra.ExactArgs(1),
		Run: func(cmd *cobra.Command, args []string) {
			username := args[0]
			dbPath, err := whatupcore2.CreateDBFilePath(username, 4)
			fmt.Println("Database file located at:", dbPath)
			if err != nil {
				fmt.Println("Could not infer DB file name from username:", err)
				defer os.Exit(1)
				return
			}
			if _, err := os.Stat(dbPath); err != nil {
				fmt.Println("Could not access file", err)
				defer os.Exit(2)
				return
			}
			if err = whatupcore2.ClearFileAndParents(dbPath); err != nil {
				fmt.Println("Could not delete database:", err)
				defer os.Exit(3)
				return
			}
			os.Exit(0)
		},
	}
)

func init() {
	rootCmd.AddCommand(whatsUpRemoveUserCmd)
}
