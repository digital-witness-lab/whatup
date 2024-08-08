package whatupcore2

import (
	"fmt"

	"github.com/digital-witness-lab/whatup/whatupcore2/pkg/whatupcore2"
	"github.com/spf13/cobra"
)

var (
	Port          uint32
	LogLevel      string
	DBUri         string
	PhotoCopUri   string
	whatsUpRPCCmd = &cobra.Command{
		Use:     "rpc",
		Aliases: []string{"r"},
		Short:   "Start a WhatUp RPC Server",
		Long:    "",
		Args:    cobra.NoArgs,
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Println("Starting RPC server on port:", Port)
			if DBUri == "" {
				DBUri = getDbUriFromEnv()
			}
			if PhotoCopUri == "" {
				PhotoCopUri = getPhotoCopUriFromEnv()
			}
			whatupcore2.StartRPC(Port, DBUri, PhotoCopUri, LogLevel)
		},
	}
)

func init() {
	// TODO: have DB path be a config variable / flag
	whatsUpRPCCmd.Flags().Uint32VarP(&Port, "port", "p", 3447, "Port for RPC server")
	whatsUpRPCCmd.Flags().StringVarP(&LogLevel, "log-level", "l", "INFO", "Logging level. One of DEBUG/INFO/WARN/ERROR")
	whatsUpRPCCmd.Flags().StringVarP(&DBUri, "db-uri", "d", "", "URI to database. If none is set, this field will be populated by envvars ")
	whatsUpRPCCmd.Flags().StringVarP(&PhotoCopUri, "photo-cop-uri", "c", "", "URI to photo cop rpc service. if empty, no photocop features are used")
	rootCmd.AddCommand(whatsUpRPCCmd)
}
