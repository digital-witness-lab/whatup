all: whatupcore.pb.go whatupcore_pb2.py
.PHONY: all clean client


whatupcore.pb.go: whatupcore.proto
	protoc \
		--go_out=. \
		--go_opt paths=source_relative \
		--go-grpc_out=. \
		--go-grpc_opt=paths=source_relative \
		*.proto 
	go mod tidy

whatupcore_pb2.py: whatupcore.proto
	protoc \
		--python_out=. \
		*.proto 

client:
	go install github.com/ktr0731/evans@v0.10.11
	evans --port 3447 --tls --cert ../data/keys/cert.pem --certkey ../data/keys/key.pem --servername localhost --proto *.proto

clean:
	rm -rf *.pb.go *_pb2.py
