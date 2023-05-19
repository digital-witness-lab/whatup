all: proto_go/github.com/digital-witness-lab/whatup/protos/whatupcore/whatupcore.pb.go proto_py/whatupcore_pb2.py
.PHONY: all clean

proto_go/github.com/digital-witness-lab/whatup/protos/whatupcore/whatupcore.pb.go: whatupcore.proto
	mkdir -p ./proto_go/
	protoc --go_out=./proto_go/ whatupcore.proto 

proto_py/whatupcore_pb2.py: whatupcore.proto
	mkdir -p ./proto_py/
	protoc --python_out=./proto_py/ whatupcore.proto 

clean:
	rm -rf ./proto_py/ ./proto_go/
