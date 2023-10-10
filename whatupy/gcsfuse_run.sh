#!/usr/bin/env bash
set -eo pipefail

echo "Mounting $SESSIONS_BUCKET bucket using GCS Fuse."
gcsfuse --debug_gcs --debug_fuse "$SESSIONS_BUCKET" "${BUCKET_MNT_DIR_PREFIX}/${SESSIONS_BUCKET_MNT_DIR}"

if [ -z "${MESSAGE_ARCHIVE_BUCKET:-}" ]; then
    echo "Mounting $MESSAGE_ARCHIVE_BUCKET bucket using GCS Fuse."
    gcsfuse --debug_gcs --debug_fuse "$MESSAGE_ARCHIVE_BUCKET" "${BUCKET_MNT_DIR_PREFIX}/${MESSAGE_ARCHIVE_BUCKET_MNT_DIR}"
fi

echo "Mounting completed."

# Start the application
/whatupy $@ &

# Exit immediately when one of the background processes terminate.
wait -n
