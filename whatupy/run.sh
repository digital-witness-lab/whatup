#!/usr/bin/env bash
set -eo pipefail

app_command=$1

if [ -z "${app_command:-}" ]; then
    echo "App command is required as an argument."
    exit 1
fi

echo "Running app command: $app_command"

case $app_command in

    archivebot)
        exec whatupy --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            --debug \
            archivebot \
            --archive-dir "gs://${MESSAGE_ARCHIVE_BUCKET}/" \
            "kek+gs://${SESSIONS_BUCKET}/"
    ;;

    databasebot)
        exec whatupy --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            databasebot \
            --database-url "${DATABASE_URL}" \
            "kek+gs://${SESSIONS_BUCKET}/" 
    ;;

    registerbot)
        exec whatupy --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            --debug \
            registerbot \
            --database-url "${DATABASE_URL}" \
            --sessions-url "kek+gs://${SESSIONS_BUCKET}/${SESSIONS_USER_SUBDIR}/" \
            "kek+gs://${SESSIONS_BUCKET}/${ONBOARD_BOT}.json"
    ;;

    onboard)
        if [ -z "${WHATUPY_ONBOARD_BOT_NAME:-}" ]; then
            echo "WHATUPY_ONBOARD_BOT_NAME env var is required."
            exit 1
        fi
        exec whatupy --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            onboard \
            --default-group-permission READWRITE  \
            --credentials-url "kek+gs://${SESSIONS_BUCKET}/" \
            "${WHATUPY_ONBOARD_BOT_NAME}"
    ;;

    load-archive)
        ( gsutil ls "gs://${MESSAGE_ARCHIVE_BUCKET}/" | xargs -n 1 -P 6 -I{} whatupy databasebot-load-archive --database-url ${DATABASE_URL} '{}/*_*.json' )
        exit $?
    ;;

    *)
        echo "Unknown app command $app_command"
        exit 1
    ;;

esac
