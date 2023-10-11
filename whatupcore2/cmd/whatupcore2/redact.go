package whatupcore2

import (
	"fmt"
	"io"
	"os"

	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/reflect/protoreflect"
	"google.golang.org/protobuf/reflect/protoregistry"

	"github.com/digital-witness-lab/whatup/whatupcore2/pkg/whatupcore2"
	"github.com/spf13/cobra"
)

var (
	MessageTypeString string
	whatsUpRedactCmd  = &cobra.Command{
		Aliases: []string{"r"},
		Use:     "redact [filename]",
		Short:   "redact JSON files containing WhatUpCore Proto Messages",
		Long:    "filename can either be a valid file or - for stdin",
		Args:    cobra.ExactArgs(1),
		Run: func(cmd *cobra.Command, args []string) {
			filename := args[0]

			var data []byte
			var err error

			if filename == "-" {
				data, err = io.ReadAll(os.Stdin)
				if err != nil {
					fmt.Fprintf(os.Stderr, "Could not from STDIN: %s\n", err)
					os.Exit(128)
					return
				}
			} else {
				data, err = os.ReadFile(filename)
				if err != nil {
					fmt.Fprintf(os.Stderr, "Could not read file: %s: %s\n", filename, err)
					os.Exit(128)
					return
				}
			}

			messageTypeAbs := fmt.Sprintf("protos.%s", MessageTypeString)
			fullName := protoreflect.FullName(messageTypeAbs)
			t, err := protoregistry.GlobalTypes.FindMessageByName(fullName)
			if err != nil {
				fmt.Fprintf(os.Stderr, "Could not find reference to message type: %s: %s: %s\n", MessageTypeString, fullName, err)
				os.Exit(128)
				return
			}

			message := t.New().Interface()
			err = protojson.Unmarshal(data, message)
			if err != nil {
				fmt.Fprintf(os.Stderr, "Could not parse json file: %s: %s: %s\n", filename, messageTypeAbs, err)
				os.Exit(128)
				return
			}

			anonLookup := whatupcore2.NewAnonLookupEmpty()
			messageRedacted := whatupcore2.AnonymizeInterface(anonLookup, message)
			messageRedactedBytes, err := protojson.Marshal(messageRedacted)
			if err != nil {
				fmt.Fprintf(os.Stderr, "Could not marshal redacted message to json: %s\n", err)
				os.Exit(128)
				return
			}

			fmt.Print(string(messageRedactedBytes))
		},
	}
	whatsUpRedactStringCmd = &cobra.Command{
		Aliases: []string{"rs"},
		Use:     "redact-string [string]",
		Short:   "Redacts a string",
		Long:    "",
		Args:    cobra.ExactArgs(1),
		Run: func(cmd *cobra.Command, args []string) {
			clear := args[0]
			fmt.Printf(whatupcore2.AnonymizeString(clear))
		},
	}
)

func init() {
	whatsUpRedactCmd.Flags().StringVarP(&MessageTypeString, "message-type", "m", "WUMessage", "Type of Message. See whatupcore.proto for available message types.")
	rootCmd.AddCommand(whatsUpRedactCmd)
	rootCmd.AddCommand(whatsUpRedactStringCmd)
}
