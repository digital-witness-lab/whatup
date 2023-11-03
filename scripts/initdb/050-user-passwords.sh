#!/bin/bash

set -e
set -u

function set_user_password() {
    local user=$1
    local password=$2
    echo "  Setting user password $user"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        ALTER USER $user WITH PASSWORD '$password';
EOSQL
}

for passwdfile in $( find /run/secrets/ -name postgres-\*-passwd ); do
    username=$(basename $passwdfile | cut -d- -f2)
    password=$( cat $passwdfile | xargs echo -n )
    if [ "$username" != "$POSTGRES_USER" ]; then
        set_user_password $username $password
    fi
done
