
certs:
	openssl req -config ./data/keys/config.conf -newkey rsa:4096 -new -nodes -x509 -days 3650 -keyout ./data/keys/key.pem -out ./data/keys/cert.pem

