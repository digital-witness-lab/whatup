.PHONY: clean build

build:
	GOOS=linux go build \
    	-o log-cleaner \
    	cleaners.go main.go

clean:
	rm -rf ./log-cleaner
