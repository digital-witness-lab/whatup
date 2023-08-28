#!/bin/bash

PG_URI=$1
MEDIA_BUCKET=${2:-whatup-media-static}
DATASET_NAME=${3:-messages}
TABLE_NAMES=(reactions group_info group_participants messages_seen messages)

TMPDIR="$(mktemp -d)"
trap 'rm -rf -- "$MYTMPDIR"' EXIT

function nested-dir() {
    fname=$1
    echo ${fname:0:1}/${fname:1:1}/${fname:2:1}/${fname:3:1}
}

for TABLE in ${TABLE_NAMES[@]}; do
    TABLE_FNAME=${TMPDIR}/${TABLE}.csv
    echo "Exporting table ${TABLE}"
    psql "${PG_URI}" -c "COPY ${TABLE} TO STDOUT WITH CSV DELIMITER ',' QUOTE '\"' ENCODING 'UTF8' HEADER" | pv > ${TABLE_FNAME}
    echo "Uploading to bigquery"
    bq load --source_format CSV --replace --allow_quoted_newlines --autodetect ${DATASET_NAME}.${TABLE} ${TABLE_FNAME}
    rm ${TABLE_FNAME}
done

# TODO: export media such that bigquery has a reference to the gcs object
TABLE=media
TABLE_FNAME=${TMPDIR}/${TABLE}.csv

