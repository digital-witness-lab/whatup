package main

import (
	"path"

	"github.com/joho/godotenv"

	"github.com/digital-witness-lab/whatup/whatupcore2/cmd/whatupcore2"
)

func main() {
	if err := godotenv.Load(path.Join("/", "tmp", "whatup", ".env")); err != nil {
		// Note: godotenv will NOT return an err if the .env file is not found.
		panic(err)
	}

	whatupcore2.Execute()
}
