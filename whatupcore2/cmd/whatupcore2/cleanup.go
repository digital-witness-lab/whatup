package whatupcore2

import (
	"database/sql"
	"fmt"
	"os"

	"github.com/digital-witness-lab/whatup/whatupcore2/pkg/encsqlstore"
	"github.com/digital-witness-lab/whatup/whatupcore2/pkg/whatupcore2"
	"github.com/spf13/cobra"
)

var (
	RUDBUri              string
	whatsUpRemoveUserCmd = &cobra.Command{
		Aliases: []string{"r"},
		Use:     "remove-user username [username...]",
		Short:   "Removes session data for user",
		Args:    cobra.MinimumNArgs(1),
		Run: func(cmd *cobra.Command, args []string) {
			if RUDBUri == "" {
				RUDBUri = getDbUriFromEnv()
			}

			db, err := sql.Open("postgres", RUDBUri)
			defer db.Close()
			if err != nil {
				fmt.Printf("Could not create encsqlstore: %w\n", err)
				return
			}

			for _, username := range args {
				fmt.Printf("Deleting user: %s\n", username)
				err = encsqlstore.DeleteUsername(db, username)
				if err != nil {
					fmt.Printf("Could not delete user: %w\n", err)
					return
				}
				acls := whatupcore2.NewACLStore(db, username, nil)
				acls.Delete()
			}
			os.Exit(0)
		},
	}
)

func init() {
	whatsUpRemoveUserCmd.Flags().StringVarP(&RUDBUri, "db-uri", "d", "", "URI to database. If none is set, this field will be populated by envvars ")
	rootCmd.AddCommand(whatsUpRemoveUserCmd)
}
