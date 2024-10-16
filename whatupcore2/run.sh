#!/usr/bin/env bash
set -eo pipefail

RAND="aajsdkhfkasjdfhsadkfhdsjfsadffhnaks"
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
if [ -e /tmp/whatup/.env ]; then
    set -o allexport
    source /tmp/whatup/.env 
    set +o allexport
fi

# Start the application
case $app_command in
    rpc)
        echo "Starting whatupcore2..."
        exec /log-cleaner /whatupcore2 $@
    ;;

    remove-user)
        if [ -z "${WHATUPCORE2_REMOVE_USER:-}" ]; then
            echo "WHATUPCORE2_REMOVE_USER env var is required."
            exit 1
        fi
        echo "Removing users ${WHATUPCORE2_REMOVE_USER}..."
        exec /log-cleaner /whatupcore2 remove-user ${WHATUPCORE2_REMOVE_USER}
    ;;

    remove-burners)
        echo "Removing burners..."
        exec /log-cleaner /whatupcore2 remove-burners
    ;;
esac
