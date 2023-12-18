#!/usr/bin/env bash
set -eo pipefail

RANDOM="348u9283yf9823rh8239"
app_command=$1

if [ -z "${app_command:-}" ]; then
    echo "App command is required as an argument."
    exit 1
fi

DEBUG=$( [[ "$IS_PROD" == "False" ]] && echo "--debug" || echo "" )
echo "Running app command: $app_command $DEBUG"

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
            --sessions-url "kek+gs://${SESSIONS_BUCKET}/${SESSIONS_USER_SUBDIR}/" \
            "kek+gs://${SESSIONS_BUCKET}/${ONBOARD_BOT}.json"
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

    *)
        echo "Unknown app command $app_command"
        exit 1
    ;;

esac
