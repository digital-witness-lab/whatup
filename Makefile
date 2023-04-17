
certs:
	openssl req -newkey rsa:4096 -new -nodes -x509 -days 3650 -keyout ./static/key.pem -out ./static/cert.pem

