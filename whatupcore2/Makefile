.PHONY: whatupcore2

whatupcore2:
	+$(MAKE) -C ../protos/ all
	go build -tags=sqlcipher .

connect: whatupcore2
	./whatupcore2 connect
