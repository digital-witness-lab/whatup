#!/bin/bash
set -eo pipefail

export CLOUDPATHLIB_FILE_CACHE_MODE="close_file"
exec hash-gen --database-id ${DATABASE_URL}
