.PHONY: connect clean whatupcore2

whatupcore2:
	go mod tidy
	go build -tags=sqlcipher main.go

connect: whatupcore2
	./whatupcore2 connect

clean:
	rm -rf ./whatupcore2
