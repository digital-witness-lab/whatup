#!/usr/bin/env bash
set -eo pipefail

app_command=$1

echo "Starting whatupcore2..."

# Start the application
case $app_command in
    rpc)
        eval /whatupcore2 $@
    ;;

    remove-user)
        if [ -z "${WHATUPCORE2_REMOVE_USER:-}" ]; then
            echo "WHATUPCORE2_REMOVE_USER env var is required."
            exit 1
        fi
        eval /whatupcore2 remove-user ${WHATUPCORE2_REMOVE_USER}
    ;;
esac


# Exit immediately when one of the background processes terminate.
wait -n
