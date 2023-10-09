#!/usr/bin/env bash
set -eo pipefail

if [ -z "${MNT_DIR:-}" ]; then
    echo "MNT_DIR is required"
    exit 1
fi

# Create mount directory for service
mkdir -p $MNT_DIR

echo "Mounting $WHATUPCORE2_BUCKET using GCS Fuse."
gcsfuse --debug_gcs --debug_fuse "$WHATUPCORE2_BUCKET" $MNT_DIR
echo "Mounting completed."

# Start the application
/whatupcore2 rpc $@ &

# Exit immediately when one of the background processes terminate.
wait -n
