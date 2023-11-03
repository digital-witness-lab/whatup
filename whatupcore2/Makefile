.PHONY: connect clean whatupcore2

whatupcore2:
	GOOS=linux go build \
    	-o whatupcore2 \
    	main.go

connect: whatupcore2
	./whatupcore2 connect

clean:
	rm -rf ./whatupcore2
