#!/bin/bash
set -eo pipefail

exec hash-gen \
    --database-url ${DATABASE_URL}