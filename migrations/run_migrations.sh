#!/bin/bash

set -eo pipefail

echo "Running migrations..."

ENCODED_DATABASE_ROOT_PASSWORD=$(echo "$DATABASE_ROOT_PASSWORD" | python3 -c 'import urllib.parse; print(urllib.parse.quote(input(), ""))')

if [ -z "${ENCODED_DATABASE_ROOT_PASSWORD:-}" ]; then
    echo "Encoded DB password is empty..."
    exit 1
fi

migrate -path /migrations -database postgres://$DATABASE_USER:$ENCODED_DATABASE_ROOT_PASSWORD@$DATABASE_HOST:5432/$DATABASE up

echo "DB migrations executed successfully!"
