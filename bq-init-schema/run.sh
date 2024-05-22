#!/bin/bash
set -eo pipefail

check_vars()
{
    var_names=("$@")
    for var_name in "${var_names[@]}"; do
        [ -z "${!var_name}" ] && echo "$var_name is unset." && var_unset=true
    done
    [ -n "$var_unset" ] && exit 1
    return 0
}

check_vars TABLES BQ_DATASET_ID BQ_PSQL_CONNECTION

echo "Setting schema for tables: $TABLES"
for TABLE in ${TABLES//,/ }; do
    if bq query --use_legacy_sql=false "SELECT * FROM EXTERNAL_QUERY('${BQ_PSQL_CONNECTION}', 'SELECT * FROM ${TABLE} LIMIT 1;');" > /dev/null; then
        echo "Setting table schema from $TABLE"
        bq query \
            --destination_table ${BQ_DATASET_ID}.${TABLE} \
            --append_table \
            --schema_update_option=ALLOW_FIELD_ADDITION \
            --schema_update_option=ALLOW_FIELD_RELAXATION \
            --use_legacy_sql=false \
                "SELECT * FROM EXTERNAL_QUERY('${BQ_PSQL_CONNECTION}', 'SELECT * FROM ${TABLE} LIMIT 500;');" \
            > /dev/null
    else
        echo "Could not transfer from table: ${TABLE}"
    fi
done
