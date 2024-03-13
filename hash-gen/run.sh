#!/bin/bash
set -eo pipefail

export CLOUDPATHLIB_FILE_CACHE_MODE="close_file"

JOB_COUNT=${CLOUD_RUN_TASK_COUNT:=1}
JOB_IDX=${CLOUD_RUN_TASK_INDEX:=0}

exec hash-gen \
    --dataset-id ${PROJECT_ID}.${DATASET_ID} \
    --job-idx $JOB_IDX \
    --job-count $JOB_COUNT
