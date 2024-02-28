package main

import (
	"fmt"
	"io/fs"
	"path"

	"github.com/joho/godotenv"

	"github.com/digital-witness-lab/whatup/whatupcore2/cmd/whatupcore2"
)

func main() {
	p := path.Join("/", "tmp", "whatup", ".env")
	fmt.Printf("Loading vars from .env file %s if it's there...\n", p)
	if err := godotenv.Load(p); err != nil {
        switch err.(type) {
        case *fs.PathError:
            fmt.Println("Could not find .env file")
        default:
	        panic(err)
        }
	}

	whatupcore2.Execute()
}
