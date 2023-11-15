.PHONY: connect clean whatupcore2

whatupcore2:
	GOOS=linux go build \
    	-o whatupcore2 \
    	main.go

connect: whatupcore2
	./whatupcore2 connect

test: test-whatupcore2 test-encsqlstore

test-whatupcore2:
	go test -v ./pkg/whatupcore2

test-encsqlstore:
	go test -v ./pkg/encsqlstore

clean:
	rm -rf ./whatupcore2
