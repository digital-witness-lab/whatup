all: whatupcore.pb.go whatupcore_pb2.py
.PHONY: all clean


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

clean:
	rm -rf *.pb.go *_pb2.py
