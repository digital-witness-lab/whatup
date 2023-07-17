ALL: certs
.PHONY: certs clean

certs:
	openssl req -config config.conf -newkey rsa:4096 -new -nodes -x509 -days 3650 -keyout key.pem -out cert.pem

clean:
	rm -rf key.pem cert.pem
