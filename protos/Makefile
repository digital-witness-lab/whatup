all: whatupcore.pb.go whatupcore_pb2.py
.PHONY: all clean client client-ssl evans

EVANS_PARAMS := --host 127.0.0.1 --port 3447 --proto whatupcore.proto


whatupcore.pb.go: whatupcore.proto
	protoc \
		--go_out=. \
		--go_opt paths=source_relative \
		--go-grpc_out=. \
		--go-grpc_opt=paths=source_relative \
		whatupcore.proto 
	go mod tidy

whatupcore_pb2.py: whatupcore.proto
	protoc \
		--python_out=. \
		whatupcore.proto 

evans:
	go install github.com/ktr0731/evans@v0.10.11

test/fiber_bearer.txt: test/fiber.json
	evans --host 127.0.0.1 --port 3447 --proto whatupcore.proto cli call --file test/fiber.json protos.WhatUpCoreAuth.Login | jq -r '.token' > test/fiber_bearer.txt

client-login-history: test/fiber.json
	evans --host 127.0.0.1 --port 3447 --proto whatupcore.proto cli call --file test/fiber.json protos.WhatUpCoreAuth.LoginWithHistory

client-auth-ssl: evans
	evans --tls --cert ../data/keys/cert.pem --certkey ../data/keys/key.pem --servername localhost ${EVANS_PARAMS} repl

client-auth: evans test/fiber_bearer.txt
	evans --header Authorization="bearer $(file < ./test/fiber_bearer.txt)" ${EVANS_PARAMS} repl --service WhatUpCore

client:
	evans ${EVANS_PARAMS} repl --service WhatUpCore

clean:
	rm -rf *.pb.go *_pb2.py ./test/*_bearer.txt
