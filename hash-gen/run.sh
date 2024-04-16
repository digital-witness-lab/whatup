#!/bin/bash
set -eo pipefail

export CLOUDPATHLIB_FILE_CACHE_MODE="close_file"
export CLOUPATHLIB_FILE_CACHE_MODE="close_file"

JOB_COUNT=${CLOUD_RUN_TASK_COUNT:=1}
JOB_IDX=${CLOUD_RUN_TASK_INDEX:=0}

echo "Running as $JOB_IDX / $JOB_COUNT"

exec hash-gen bulk-to-bigquery \
    --hash-table phash_images \
    --media-table media \
    --dataset-id ${PROJECT_ID}.${DATASET_ID} \
    --job-idx $JOB_IDX \
    --job-count $JOB_COUNT
