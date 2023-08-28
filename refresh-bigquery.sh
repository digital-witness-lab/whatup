#!/bin/bash

PG_URI=$1
MEDIA_BUCKET=${2:-whatup-media-static}
DATASET_NAME=${3:-messages}
DB_NAME=db$( openssl rand -hex 8 )
CONTAINER=

function cleanup() {
    echo "Stopping container if it exists"
    docker stop --time 5 "${DB_NAME}"
    docker container rm "${DB_NAME}"

    echo "Removing database: ${DB_NAME}"
    psql ${PG_URI} -c "DROP DATABASE IF EXISTS ${DB_NAME}"
}

echo "Creating database: ${DB_NAME}"
psql ${PG_URI} -c "CREATE DATABASE ${DB_NAME}"
trap cleanup EXIT

echo "Loading archive"
docker compose run --detach --build -e POSTGRES_DATABASE=${DB_NAME} --name=${DB_NAME} bot-database-load-archive
time docker wait ${DB_NAME}

echo "Uploading archive to BigQuery"
./scripts/postgres-export-bigquery.sh "${PG_URI%%/}/${DB_NAME}" "${MEDIA_BUCKET}" "${DATASET_NAME}"

cleanup
