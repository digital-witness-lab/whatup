#!/usr/bin/env bash
set -eo pipefail

RAND="234i5u3oifjsdffiusdsdff"
app_command=$1

if [ -z "${app_command:-}" ]; then
    echo "App command is required as an argument."
    exit 1
fi

DEBUG=
#$( [[ "$IS_PROD" == "False" ]] && echo "--debug" || echo "" )
echo "Running app command: $app_command $DEBUG"

# Run the VM secrets configurator.
# If we are not running inside a VM,
# it will exit silently.
/configureVmSecrets

function positive_mod() {
    local dividend=$1
    local divisor=$2
    printf "%d" $(( (($dividend % $divisor) + $divisor) % $divisor ))
}

function filter-by-job() {
    local idx=$1
    local n_jobs=$2
    while read LINE; do
        local hash_str=$( echo $LINE | sha1sum - | cut -f1 -d' ' );
        local hash_dec=$((0x$hash_str));
        local mod=$( positive_mod $hash_dec $n_jobs )
        [[ $mod == $idx ]] && echo $LINE;
    done
    exit 0
}
export -f filter-by-job

case $app_command in

    archivebot)
        exec whatupy $DEBUG --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            archivebot \
            --archive-dir "gs://${MESSAGE_ARCHIVE_BUCKET}/" \
            "kek+gs://${SESSIONS_BUCKET}/users/"
    ;;

    databasebot)
        exec whatupy $DEBUG --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            databasebot \
            --database-url "${DATABASE_URL}" \
            --media-base "gs://${MEDIA_BUCKET}/" \
            "kek+gs://${SESSIONS_BUCKET}/users/" 
    ;;

    registerbot)
        exec whatupy $DEBUG --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            registerbot \
            --database-url "${DATABASE_URL}" \
            --sessions-url "kek+gs://${SESSIONS_BUCKET}/users/" \
            "kek+gs://${SESSIONS_BUCKET}/${PRIMARY_BOT_NAME}.json"
    ;;

    userservices)
        exec whatupy $DEBUG --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            userservicesbot \
            --database-url "${DATABASE_URL}" \
            --sessions-url "kek+gs://${SESSIONS_BUCKET}/users/" \
            --public-path "gs://${TEMP_BUCKET}/" \
            "kek+gs://${SESSIONS_BUCKET}/${PRIMARY_BOT_NAME}.json"
    ;;

    onboard)
        if [ -z "${WHATUPY_ONBOARD_BOT_NAME:-}" ]; then
            echo "WHATUPY_ONBOARD_BOT_NAME env var is required."
            exit 1
        fi
        exec whatupy $DEBUG --host "${WHATUPCORE2_HOST}" \
            --port 443 \
            onboard \
            --default-group-permission READWRITE  \
            --credentials-url "kek+gs://${SESSIONS_BUCKET}/" \
            "${WHATUPY_ONBOARD_BOT_NAME}"
    ;;

    load-archive)
        n_jobs=${CLOUD_RUN_TASK_COUNT:=1}
        idx=${CLOUD_RUN_TASK_INDEX:=0}
        echo "Loading archive: Job $idx out of $n_jobs"

        whatupy gs-ls "gs://${MESSAGE_ARCHIVE_BUCKET}/" | \
            filter-by-job $idx $n_jobs | \
            tee /dev/stderr | \
            xargs -P 2 -I{} \
                whatupy $DEBUG \
                    databasebot-load-archive \
                    --database-url ${DATABASE_URL} \
                    --media-base "gs://${MEDIA_BUCKET}/" \
                    '{}/*_*.json' 
        retval=$?
        echo "Exiting run.sh with code: $retval"
        exit $retval
    ;;

    delete-groups)
        if [ -z "${WHATUPY_DELETE_GROUPS:-}" ]; then
            echo "WHATUPY_DELETE_GROUPS env var is required."
            exit 1
        fi
        exec whatupy $DEBUG \
            databasebot-delete-groups \
                    --database-url ${DATABASE_URL} \
                    --media-base "gs://${MEDIA_BUCKET}/" \
                    "${WHATUPY_DELETE_GROUPS}"
    ;;

    *)
        echo "Unknown app command $app_command"
        exit 1
    ;;

esac
