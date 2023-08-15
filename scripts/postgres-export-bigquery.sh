#!/bin/bash

PG_URI=$1
DATASET_NAME=${2:-messages}
TABLE_NAMES=(reactions group_info group_participants messages media)

TMPDIR="$(mktemp -d)"
trap 'rm -rf -- "$MYTMPDIR"' EXIT

for TABLE in ${TABLE_NAMES[@]}; do
    TABLE_FNAME=${TMPDIR}/${TABLE}.csv
    echo "Exporting table ${TABLE}"
    psql "${PG_URI}" -c "COPY ${TABLE} TO STDOUT WITH CSV DELIMITER ',' QUOTE '\"' ENCODING 'UTF8' HEADER" | pv > ${TABLE_FNAME}
    echo "Uploading to bigquery"
    bq load --source_format CSV --replace --allow_quoted_newlines --autodetect ${DATASET_NAME}.${TABLE} ${TABLE_FNAME}
    rm ${TABLE_FNAME}
done

