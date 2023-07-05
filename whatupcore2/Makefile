.PHONY: connect clean whatupcore2

whatupcore2:
	+$(MAKE) -C ../protos/ all
	go mod tidy
	go build -tags=sqlcipher .

connect: whatupcore2
	./whatupcore2 connect

clean:
	rm -rf ./whatupcore2
