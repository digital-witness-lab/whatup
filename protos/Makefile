all: ../whatupcore2/protos/whatupcore.pb.go ../whatupcore2/protos/photo_cop.pb.go ../whatupy/whatupy/whatupcore_pb2_grpc.py ../photo-cop/src/main/proto/photo_cop.proto
.PHONY: all clean client client-ssl evans

EVANS_PARAMS := --host 127.0.0.1 --port 3447 --proto whatupcore.proto
EVANS_SSL_PARAMS := --tls --cert ../data/keys/cert.pem --certkey ../data/keys/key.pem --servername localhost


../photo-cop/src/main/proto/photo_cop.proto: photo_cop.proto
	cp photo_cop.proto ../photo-cop/src/main/proto/photo_cop.proto

../whatupcore2/protos/photo_cop.pb.go: photo_cop.proto
	protoc \
		--go_out=../whatupcore2/protos/ \
		--go_opt paths=source_relative \
		--go-grpc_out=../whatupcore2/protos/ \
		--go-grpc_opt=paths=source_relative \
		photo_cop.proto 
	cd ../whatupcore2/protos/ ; go mod tidy

../whatupcore2/protos/whatupcore.pb.go: whatupcore.proto
	protoc \
		--go_out=../whatupcore2/protos/ \
		--go_opt paths=source_relative \
		--go-grpc_out=../whatupcore2/protos/ \
		--go-grpc_opt=paths=source_relative \
		whatupcore.proto 
	cd ../whatupcore2/protos/ ; go mod tidy

../whatupy/whatupy/whatupcore_pb2_grpc.py: whatupcore.proto
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

init:
	python -m pip install protoletariat grpclib protobuf grpcio-tools mypy mypy-protobuf
	#go install github.com/ktr0731/evans@v0.10.11
