.PHONY: connect clean whatupcore2

whatupcore2:
	GOOS=linux go build \
    	-o whatupcore2 \
    	main.go

connect: whatupcore2
	./whatupcore2 connect

test: test-whatupcore2 test-encsqlstore

test-whatupcore2:
	ANON_KEY="asdf" go test -v ./pkg/whatupcore2

test-encsqlstore:
	ANON_KEY="asdf" go test -v ./pkg/encsqlstore

update-whatsmeow:
	go get -u go.mau.fi/whatsmeow

clean:
	rm -rf ./whatupcore2
