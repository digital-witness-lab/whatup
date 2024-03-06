package main

import (
	"fmt"
	"os"
	"path"

	"github.com/joho/godotenv"

	"github.com/digital-witness-lab/whatup/whatupcore2/cmd/whatupcore2"
)

func main() {
	p := path.Join("/", "tmp", "whatup", ".env")
	fmt.Printf("Loading vars from .env file %s if it's there...\n", p)
	if _, err := os.Stat(p); err == nil {
		if err := godotenv.Load(p); err != nil {
			// Note: godotenv will NOT return an err if the .env file is not found.
			panic(err)
		}
	}

	whatupcore2.Execute()
}
