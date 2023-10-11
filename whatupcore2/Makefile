.PHONY: connect clean whatupcore2

whatupcore2:
	GOOS=linux go build \
    	-tags "sqlite3 sqlcipher sqlite_secure_delete" \
    	-o whatupcore2 \
    	main.go

connect: whatupcore2
	./whatupcore2 connect

clean:
	rm -rf ./whatupcore2
