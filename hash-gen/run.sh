#!/bin/bash
set -eo pipefail

exec whatupy $DEBUG \
    hash-gen \
        --bucket-dir ${DATABASE_URL}