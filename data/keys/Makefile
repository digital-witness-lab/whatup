ALL: whatup photocop
.PHONY: ALL whatup photocop clean

whatup: whatup.key.pem whatup.cert.pem
photocop: photocop.key.pem photocop.cert.pem


%.key.pem %.cert.pem: %.config.conf
	openssl req -config $< -newkey rsa:4096 -new -nodes -x509 -days 3650 -keyout $*.key.pem -out $*.cert.pem

clean:
	rm -rf *.key.pem *.cert.pem
