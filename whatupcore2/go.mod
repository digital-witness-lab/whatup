module github.com/digital-witness-lab/whatup/whatupcore2

go 1.19

require (
	github.com/alexedwards/argon2id v0.0.0-20230305115115-4b3c3280a736
	github.com/digital-witness-lab/whatup/protos v0.0.0-00010101000000-000000000000
	github.com/golang-jwt/jwt/v5 v5.0.0
	github.com/grpc-ecosystem/go-grpc-middleware/v2 v2.0.0-rc.5
	github.com/lib/pq v1.10.9
	github.com/mitchellh/mapstructure v1.5.0
	github.com/nyaruka/phonenumbers v1.1.8
	github.com/spf13/cobra v1.7.0
	go.mau.fi/whatsmeow v0.0.0-20240106083317-757651400d8d
	google.golang.org/grpc v1.56.0
	google.golang.org/protobuf v1.32.0
)

require (
	filippo.io/edwards25519 v1.1.0 // indirect
	github.com/golang/protobuf v1.5.3 // indirect
	github.com/gorilla/websocket v1.5.1 // indirect
	github.com/hashicorp/golang-lru/v2 v2.0.7 // indirect
	github.com/inconshreveable/mousetrap v1.1.0 // indirect
	github.com/mattn/go-sqlite3 v1.14.18 // indirect
	github.com/spf13/pflag v1.0.5 // indirect
	go.mau.fi/libsignal v0.1.0 // indirect
	go.mau.fi/util v0.2.1 // indirect
	golang.org/x/crypto v0.17.0 // indirect
	golang.org/x/exp v0.0.0-20231110203233-9a3e6036ecaa // indirect
	golang.org/x/net v0.19.0 // indirect
	golang.org/x/sys v0.15.0 // indirect
	golang.org/x/text v0.14.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20230530153820-e85fd2cbaebc // indirect
)

replace github.com/digital-witness-lab/whatup/protos => ./protos/
