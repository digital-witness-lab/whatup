#!/bin/bash

set -eo pipefail

echo "Running migrations..."

ENCODED_DATABASE_URL=$(python3 -c 'import urllib.parse; print(urllib.parse.quote(input("${DATABASE_URL}"), ""))')

migrate -path /migrations -database ${ENCODED_DATABASE_URL} up

echo "DB migrations executed successfully!"
