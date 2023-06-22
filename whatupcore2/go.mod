module github.com/digital-witness-lab/whatup/whatupcore2

go 1.19

require (
	github.com/digital-witness-lab/whatup/protos v0.0.0-00010101000000-000000000000
	github.com/golang-jwt/jwt/v5 v5.0.0
	github.com/mattn/go-sqlite3 v1.14.17
	github.com/mdp/qrterminal/v3 v3.1.1
	github.com/spf13/cobra v1.7.0
	go.mau.fi/whatsmeow v0.0.0-20230616194828-be0edabb0bf3
	golang.org/x/term v0.9.0
	google.golang.org/grpc v1.56.0
)

require (
	filippo.io/edwards25519 v1.0.0 // indirect
	github.com/golang/protobuf v1.5.3 // indirect
	github.com/gorilla/websocket v1.5.0 // indirect
	github.com/inconshreveable/mousetrap v1.1.0 // indirect
	github.com/spf13/pflag v1.0.5 // indirect
	go.mau.fi/libsignal v0.1.0 // indirect
	golang.org/x/crypto v0.10.0 // indirect
	golang.org/x/net v0.11.0 // indirect
	golang.org/x/sys v0.9.0 // indirect
	golang.org/x/text v0.10.0 // indirect
	google.golang.org/genproto v0.0.0-20230525234025-438c736192d0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20230530153820-e85fd2cbaebc // indirect
	google.golang.org/protobuf v1.30.0 // indirect
	rsc.io/qr v0.2.0 // indirect
)

replace github.com/mattn/go-sqlite3 => github.com/mynameisfiber/go-sqlite3 v1.14.17-sqlcypher

replace github.com/digital-witness-lab/whatup/protos => ../protos
