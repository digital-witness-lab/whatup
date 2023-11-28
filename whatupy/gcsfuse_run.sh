#!/usr/bin/env bash
set -eo pipefail

app_command=$1
gcs_params=""

if [ -z "${app_command:-}" ]; then
    echo "App command is required as an argument."
    exit 1
fi

if [ -n "${MESSAGE_ARCHIVE_BUCKET:-}" ]; then
    echo "Mounting $MESSAGE_ARCHIVE_BUCKET bucket using GCS Fuse."
    mkdir -p "${BUCKET_MNT_DIR_PREFIX}/${MESSAGE_ARCHIVE_BUCKET_MNT_DIR}"
    gcsfuse ${gcs_params} "$MESSAGE_ARCHIVE_BUCKET" "${BUCKET_MNT_DIR_PREFIX}/${MESSAGE_ARCHIVE_BUCKET_MNT_DIR}"
fi

echo "Mounting completed."

echo "Running app command: $app_command"

case $app_command in

    archivebot)
        whatupy --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            archivebot \
            --archive-dir "${BUCKET_MNT_DIR_PREFIX}/${MESSAGE_ARCHIVE_BUCKET_MNT_DIR}" \
            "kek+gs://${SESSIONS_BUCKET}/" &
    ;;

    databasebot)
        whatupy --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            databasebot \
            --database-url "${DATABASE_URL}" \
            "kek+gs://${SESSIONS_BUCKET}/" &
    ;;

    registerbot)
        whatupy --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            registerbot \
            --database-url "${DATABASE_URL}" \
            --sessions-url "kek+gs://${SESSIONS_BUCKET}/${SESSIONS_USER_SUBDIR}/" \
            "kek+gs://${SESSIONS_BUCKET}/${ONBOARD_BOT}.json" &
    ;;

    onboard)
        if [ -z "${WHATUPY_ONBOARD_BOT_NAME:-}" ]; then
            echo "WHATUPY_ONBOARD_BOT_NAME env var is required."
            exit 1
        fi
        whatupy --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            onboard \
            --default-group-permission READWRITE  \
            --credentials-url "kek+gs://${SESSIONS_BUCKET}/" \
            "${WHATUPY_ONBOARD_BOT_NAME}" &
    ;;

    load-archive)
        ( ls "${BUCKET_MNT_DIR_PREFIX}/${MESSAGE_ARCHIVE_BUCKET_MNT_DIR}" | xargs -n 1 -P 6 -I{} whatupy databasebot-load-archive --database-url ${DATABASE_URL} '${BUCKET_MNT_DIR_PREFIX}/${MESSAGE_ARCHIVE_BUCKET_MNT_DIR}{}/*_*.json' ) &
    ;;

    *)
        echo "Unknown app command $app_command"
        exit 1
    ;;

esac

# Exit immediately when one of the background processes terminate.
wait -n
