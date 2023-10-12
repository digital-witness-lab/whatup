#!/usr/bin/env bash
set -eo pipefail

if [ -z "${WHATUPCORE2_BUCKET_MNT_DIR:-}" ]; then
    echo "WHATUPCORE2_BUCKET_MNT_DIR is required"
    exit 1
fi

# Create mount directory for service
mkdir -p $WHATUPCORE2_BUCKET_MNT_DIR

echo "Mounting $WHATUPCORE2_BUCKET using GCS Fuse."
gcsfuse "$WHATUPCORE2_BUCKET" $WHATUPCORE2_BUCKET_MNT_DIR
echo "Mounting completed."

# Start the application
/whatupcore2 rpc $@ &

# Exit immediately when one of the background processes terminate.
wait -n
