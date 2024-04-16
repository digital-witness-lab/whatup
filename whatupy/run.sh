#!/usr/bin/env bash
set -eo pipefail

RAND="aaksdfjasdkfsaksjdfhaskdjfdffdsdff"
app_command=$1
WHATUPY_CMD="/log-cleaner whatupy"

if [ -z "${app_command:-}" ]; then
    echo "App command is required as an argument."
    exit 1
fi

DEBUG= #$( [[ "$IS_PROD" == "False" ]] && echo "--debug" || echo "" )
echo "Running app command: $app_command $DEBUG"

# Run the VM secrets configurator.
# If we are not running inside a VM,
# it will exit silently.
/configureVmSecrets
if [ -e /tmp/whatup/.env ]; then
    set -o allexport
    source /tmp/whatup/.env 
    set +o allexport
fi

# This block is for cloud-run services/jobs
if [ -n "${SSL_CERT_PEM_B64+set}" ]; then
    mkdir -p /run/secrets/
    echo $SSL_CERT_PEM_B64 | base64 --decode > /run/secrets/ssl-cert
fi

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

# SERIOUSLY??? CLOUDPATHLIB HAS A TYPO IN THIS ENVVAR?!?!?
export CLOUPATHLIB_FILE_CACHE_MODE="close_file"
export CLOUDPATHLIB_FILE_CACHE_MODE="close_file"

case $app_command in

    archivebot)
        exec ${WHATUPY_CMD} $DEBUG --host "${WHATUPCORE2_HOST}" \
            --cert /run/secrets/ssl-cert \
            --port 3447 \
            archivebot \
            --archive-dir "gs://${MESSAGE_ARCHIVE_BUCKET}/" \
            "kek+gs://${SESSIONS_BUCKET}/users/"
    ;;

    databasebot)
        exec ${WHATUPY_CMD} $DEBUG --host "${WHATUPCORE2_HOST}" \
            --cert /run/secrets/ssl-cert \
            --port 3447 \
            databasebot \
            --database-url "${DATABASE_URL}" \
            --media-base "gs://${MEDIA_BUCKET}/" \
            "kek+gs://${SESSIONS_BUCKET}/users/" 
    ;;

    registerbot)
        exec ${WHATUPY_CMD} $DEBUG --host "${WHATUPCORE2_HOST}" \
            --cert /run/secrets/ssl-cert \
            --port 3447 \
            registerbot \
            --database-url "${DATABASE_URL}" \
            --sessions-url "kek+gs://${SESSIONS_BUCKET}/users/" \
            "kek+gs://${SESSIONS_BUCKET}/${PRIMARY_BOT_NAME}.json"
    ;;

    userservices)
        exec ${WHATUPY_CMD} $DEBUG --host "${WHATUPCORE2_HOST}" \
            --cert /run/secrets/ssl-cert \
            --port 3447 \
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
        exec ${WHATUPY_CMD} $DEBUG --host "${WHATUPCORE2_HOST}" \
            --cert /run/secrets/ssl-cert \
            --port 3447 \
            onboard \
            --default-group-permission READWRITE  \
            --credentials-url "kek+gs://${SESSIONS_BUCKET}/" \
            "${WHATUPY_ONBOARD_BOT_NAME}"
    ;;

    load-archive)
        n_jobs=${CLOUD_RUN_TASK_COUNT:=1}
        idx=${CLOUD_RUN_TASK_INDEX:=0}
        num_tasks=${NUM_TASKS:=2}
        echo "Loading archive: Job $idx out of $n_jobs"

        ${WHATUPY_CMD} gs-ls "gs://${MESSAGE_ARCHIVE_BUCKET}/" | \
            egrep "${ARCHIVE_FILTER:=.}" | \
            filter-by-job $idx $n_jobs | \
            tee /dev/stderr | \
            xargs -P ${num_tasks} -I{} \
                ${WHATUPY_CMD} $DEBUG \
                    databasebot-load-archive \
                    --database-url ${DATABASE_URL} \
                    --media-base "gs://${MEDIA_BUCKET}/" \
                    '{}/*.json' 
        retval=$?
        echo "Exiting run.sh with code: $retval"
        exit $retval
    ;;

    delete-groups)
        if [ -z "${WHATUPY_DELETE_GROUPS:-}" ]; then
            echo "WHATUPY_DELETE_GROUPS env var is required."
            exit 1
        fi
        exec ${WHATUPY_CMD} $DEBUG \
            databasebot-delete-groups \
                    --database-url ${DATABASE_URL} \
                    --media-base "gs://${MEDIA_BUCKET}/" \
                    "${WHATUPY_DELETE_GROUPS}"
    ;;

    debugbot)
        exit 1
        exec ${WHATUPY_CMD} $DEBUG --host "whatup" --cert /run/secrets/ssl-cert debugbot --host 0.0.0.0 --port 6666 /usr/src/whatupy-data/sessions/gertrude.json

    ;;

    *)
        echo "Unknown app command $app_command"
        exit 1
    ;;

esac
