#!/usr/bin/env bash
set -eo pipefail

app_command=$1

if [ -z "${app_command:-}" ]; then
    echo "App command is required as an argument."
    exit 1
fi

echo "Mounting $SESSIONS_BUCKET bucket using GCS Fuse."
# Create mount directory for service
mkdir -p "${BUCKET_MNT_DIR_PREFIX}/${SESSIONS_BUCKET_MNT_DIR}"
gcsfuse "$SESSIONS_BUCKET" "${BUCKET_MNT_DIR_PREFIX}/${SESSIONS_BUCKET_MNT_DIR}"

if [ -n "${MESSAGE_ARCHIVE_BUCKET:-}" ]; then
    echo "Mounting $MESSAGE_ARCHIVE_BUCKET bucket using GCS Fuse."
    mkdir -p "${BUCKET_MNT_DIR_PREFIX}/${MESSAGE_ARCHIVE_BUCKET_MNT_DIR}"
    gcsfuse "$MESSAGE_ARCHIVE_BUCKET" "${BUCKET_MNT_DIR_PREFIX}/${MESSAGE_ARCHIVE_BUCKET_MNT_DIR}"
fi

echo "Mounting completed."

echo "Running app command: $app_command"

case $app_command in

    archivebot)
        whatupy --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            archivebot \
            --archive-dir "${BUCKET_MNT_DIR_PREFIX}/${MESSAGE_ARCHIVE_BUCKET_MNT_DIR}" \
            "${BUCKET_MNT_DIR_PREFIX}/${SESSIONS_BUCKET_MNT_DIR}" &
    ;;

    databasebot)
        whatupy --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            databasebot \
            --database-url "${DATABASE_URL}" \
            "${BUCKET_MNT_DIR_PREFIX}/${SESSIONS_BUCKET_MNT_DIR}" &
    ;;

    onboard-bulk)
        if [ -z "${WHATUPY_ONBOARD_BOT_NAME:-}" ]; then
            echo "WHATUPY_ONBOARD_BOT_NAME env var is required."
            exit 1
        fi
        whatupy --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            onboard \
            --credentials-dir "${BUCKET_MNT_DIR_PREFIX}/${SESSIONS_BUCKET_MNT_DIR}" "${WHATUPY_ONBOARD_BOT_NAME}" &
    ;;

    *)
        echo "Unknown app command $app_command"
        exit 1
    ;;

esac

# Exit immediately when one of the background processes terminate.
wait -n
