package whatupcore2

import (
	"fmt"

	"github.com/digital-witness-lab/whatup/whatupcore2/pkg/whatupcore2"
	"github.com/spf13/cobra"
)

var (
    Port uint32
    whatsUpRPCCmd = &cobra.Command{
        Use:   "rpc",
        Aliases: []string{"r"},
        Short:  "Start a WhatUp RPC Server",
        Long: "",
        Args:  cobra.NoArgs,
        Run: func(cmd *cobra.Command, args []string) {
            fmt.Println("Starting RPC server on port:", Port)
            whatupcore2.StartRPC(Port)
        },
    }
)

func init() {
    // TODO: have DB path be a config variable / flag
    whatsUpRPCCmd.Flags().Uint32VarP(&Port, "port", "p", 3447, "Port for RPC server")
    rootCmd.AddCommand(whatsUpRPCCmd)
}

