#!/usr/bin/env bash
set -eo pipefail

RAND="89234uisdu8923uifhsdjwfhnaks"
app_command=$1
echo "Starting whatupcore2 with command $app_command."

if [ -e /run/secrets/whatupcore-anon-key ]; then
    echo "Setting ANON_KEY from docker secret"
    export ANON_KEY=$( cat /run/secrets/whatupcore-anon-key )
fi

# Run the VM secrets configurator.
# If we are not running inside a VM,
# it will exit silently.
/configureVmSecrets

# Start the application
case $app_command in
    rpc)
        exec /whatupcore2 $@
    ;;

    remove-user)
        if [ -z "${WHATUPCORE2_REMOVE_USER:-}" ]; then
            echo "WHATUPCORE2_REMOVE_USER env var is required."
            exit 1
        fi
        exec /whatupcore2 remove-user ${WHATUPCORE2_REMOVE_USER}
    ;;
esac
