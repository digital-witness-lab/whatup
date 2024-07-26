all: ../whatupcore2/protos/whatupcore.pb.go ../whatupy/whatupy/whatupcore_pb2_grpc.py
.PHONY: all clean client client-ssl evans

EVANS_PARAMS := --host 127.0.0.1 --port 3447 --proto whatupcore.proto
EVANS_SSL_PARAMS := --tls --cert ../data/keys/cert.pem --certkey ../data/keys/key.pem --servername localhost


../photo-cop/src/main/proto/photo_cop.proto: photo_cop.proto
	cp photo_cop.proto ../photo-cop/src/main/proto/photo_cop.proto

../whatupcore2/protos/whatupcore.pb.go: whatupcore.proto
	protoc \
		--go_out=../whatupcore2/protos/ \
		--go_opt paths=source_relative \
		--go-grpc_out=../whatupcore2/protos/ \
		--go-grpc_opt=paths=source_relative \
		whatupcore.proto 
	cd ../whatupcore2/protos/ ; go mod tidy

../whatupy/whatupy/whatupcore_pb2_grpc.py: whatupcore.proto
	python -m pip install protoletariat grpclib protobuf grpcio-tools mypy mypy-protobuf
	python -m grpc_tools.protoc \
		-I . \
		--python_out=../whatupy/whatupy/protos/ \
		--grpc_python_out=../whatupy/whatupy/protos/ \
		--mypy_out=../whatupy/whatupy/protos/ \
		./whatupcore.proto ./whatsappweb.proto
	python -m protoletariat \
		--create-package \
		--in-place \
		--python-out ../whatupy/whatupy/protos/ \
		protoc --proto-path=. ./whatupcore.proto ./whatsappweb.proto

evans:
	go install github.com/ktr0731/evans@v0.10.11

test/fiber_bearer.txt: test/fiber.json
	evans ${EVANS_SSL_PARAMS} ${EVANS_PARAMS} cli call --file test/fiber.json protos.WhatUpCoreAuth.Login | jq -r '.token' > test/fiber_bearer.txt

client-login-history: test/fiber.json
	evans --host 127.0.0.1 --port 3447 --proto whatupcore.proto cli call --file test/fiber.json protos.WhatUpCoreAuth.LoginWithHistory

client-auth-ssl: evans test/fiber_bearer.txt
	evans ${EVANS_SSL_PARAMS} ${EVANS_PARAMS} repl

client-auth: evans test/fiber_bearer.txt
	evans --header Authorization="bearer $(file < ./test/fiber_bearer.txt)" ${EVANS_PARAMS} repl --service WhatUpCore

client:
	evans ${EVANS_PARAMS} repl --service WhatUpCore

clean:
	rm -rf *.pb.go *_pb2.py ./test/*_bearer.txt
