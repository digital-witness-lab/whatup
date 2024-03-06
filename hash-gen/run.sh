#!/bin/bash
set -eo pipefail

exec hash-gen \
    --bucket-dir ${DATABASE_URL}