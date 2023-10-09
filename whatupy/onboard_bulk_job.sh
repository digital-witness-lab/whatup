#!/usr/bin/env bash
set -eo pipefail

echo "Mounting $SESSIONS_BUCKET bucket using GCS Fuse."
gcsfuse --debug_gcs --debug_fuse "$SESSIONS_BUCKET" "${BUCKET_MNT_DIR_PREFIX}/${SESSIONS_BUCKET_MNT_DIR}"

echo "Mounting completed."

# Start the application
whatupy --host $WHATUPCORE2_HOST onboard-bulk --credentials-dir "${BUCKET_MNT_DIR_PREFIX}/${SESSIONS_BUCKET_MNT_DIR}"
