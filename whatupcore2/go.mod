module github.com/digital-witness-lab/whatup/whatupcore2

go 1.22

require (
	github.com/alexedwards/argon2id v0.0.0-20230305115115-4b3c3280a736
	github.com/digital-witness-lab/whatup/protos v0.0.0-00010101000000-000000000000
	github.com/golang-jwt/jwt/v5 v5.0.0
	github.com/grpc-ecosystem/go-grpc-middleware/v2 v2.0.0-rc.5
	github.com/lib/pq v1.10.9
	github.com/mitchellh/mapstructure v1.5.0
	github.com/nyaruka/phonenumbers v1.1.8
	github.com/spf13/cobra v1.7.0
	go.mau.fi/whatsmeow v0.0.0-20240816195430-66c6524b93ad
	google.golang.org/grpc v1.56.0
	google.golang.org/protobuf v1.34.2
)

require (
	github.com/google/uuid v1.6.0 // indirect
	github.com/mattn/go-colorable v0.1.13 // indirect
	github.com/mattn/go-isatty v0.0.20 // indirect
	github.com/rs/zerolog v1.33.0 // indirect
)

require (
	filippo.io/edwards25519 v1.1.0 // indirect
	github.com/golang/protobuf v1.5.3 // indirect
	github.com/gorilla/websocket v1.5.3 // indirect
	github.com/hashicorp/golang-lru/v2 v2.0.7 // indirect
	github.com/inconshreveable/mousetrap v1.1.0 // indirect
	github.com/joho/godotenv v1.5.1
	github.com/mattn/go-sqlite3 v1.14.22 // indirect
	github.com/spf13/pflag v1.0.5 // indirect
	go.mau.fi/libsignal v0.1.1 // indirect
	go.mau.fi/util v0.7.0 // indirect
	golang.org/x/crypto v0.26.0 // indirect
	golang.org/x/exp v0.0.0-20240808152545-0cdaa3abc0fa // indirect
	golang.org/x/net v0.28.0 // indirect
	golang.org/x/sys v0.24.0 // indirect
	golang.org/x/text v0.17.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20230530153820-e85fd2cbaebc // indirect
)

replace github.com/digital-witness-lab/whatup/protos => ./protos/
