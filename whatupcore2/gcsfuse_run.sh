#!/usr/bin/env bash
set -eo pipefail

app_command=$1
gcs_params=""

if [ -z "${WHATUPCORE2_BUCKET_MNT_DIR:-}" ]; then
    echo "WHATUPCORE2_BUCKET_MNT_DIR is required"
    exit 1
fi

# Create mount directory for service
mkdir -p $WHATUPCORE2_BUCKET_MNT_DIR

echo "Mounting $WHATUPCORE2_BUCKET using GCS Fuse."
gcsfuse ${gcs_params} "$WHATUPCORE2_BUCKET" $WHATUPCORE2_BUCKET_MNT_DIR
echo "Mounting completed."

echo "Starting whatupcore2..."

# Start the application
case $app_command in
    rpc)
        /whatupcore2 $@ &
    ;;

    remove-user)
        if [ -z "${WHATUPCORE2_REMOVE_USER:-}" ]; then
            echo "WHATUPCORE2_REMOVE_USER env var is required."
            exit 1
        fi
        /whatupcore2 remove-user ${WHATUPCORE2_REMOVE_USER} &
    ;;
esac


# Exit immediately when one of the background processes terminate.
wait -n
