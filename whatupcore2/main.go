package main

import (
	"path"

	"github.com/joho/godotenv"

	"github.com/digital-witness-lab/whatup/whatupcore2/cmd/whatupcore2"
)

func main() {
	godotenv.Load(path.Join("/", "tmp", "whatup", ".env"))

	whatupcore2.Execute()
}
