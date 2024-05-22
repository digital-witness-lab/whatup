#!/bin/env bash

# Bucket URLs
TASK_NAME=$1
TOTAL_TASKS=$2
LOCK_BUCKET="gs://dwl-media-d9a2e8c/load-archive-lock/"
TOTAL_BUCKET="gs://dwl-msgarc-76f5b32/"

# Check for required argument TASK_NAME
if [ -z "$TASK_NAME" ]; then
    echo "Usage: $0 TASK_NAME [TOTAL_TASKS]"
    exit 1
fi

# Check if TOTAL_TASKS was provided
if [ -z "$TOTAL_TASKS" ]; then
    TOTAL_TASKS=$(gsutil ls $TOTAL_BUCKET | wc -l)
fi

# Get the date of the oldest file in the load-archive-lock bucket
oldest_file_date=$(gsutil ls -l $LOCK_BUCKET | grep "${TASK_NAME}" | grep -v "TOTAL" | awk '{print $2}' | sort | head -n 1)
start_seconds=$(date -d "$oldest_file_date" '+%s')

while true; do
    # Get the number of completed tasks
    completed_tasks=$(gsutil ls $LOCK_BUCKET${TASK_NAME}* | wc -l)
    
    # Calculate the progress percentage
    progress=$(echo "scale=2; $completed_tasks * 100.0 / $TOTAL_TASKS" | bc)
    
    # Calculate elapsed time in days since the oldest file date
    current_seconds=$(date -u '+%s')
    elapsed_seconds=$(($current_seconds - $start_seconds))
    elapsed_days=$(echo "scale=2; $elapsed_seconds/86400" | bc)
    
    # Estimate total duration and completion date
    if [ $completed_tasks -eq 0 ]; then
        echo "No tasks have been completed yet. Cannot estimate completion time."
    else
        total_duration_seconds=$(echo "scale=2; $elapsed_seconds/$completed_tasks*$TOTAL_TASKS" | bc)
        remaining_days=$(echo "scale=2; $total_duration_seconds - $elapsed_seconds" | bc)
        estimated_completion_date=$(date -d "+$remaining_days seconds" )
    fi
    
    # Output the progress
    echo "Progress: $progress% ($completed_tasks/$TOTAL_TASKS)"
    echo "Started on: $oldest_file_date"
    echo "Current date: $( date -u +"%Y-%m-%dT%H:%M:%SZ" )"
    echo "Estimated completion date: $estimated_completion_date"

    ntfy send load-archive "Progress: $progress% ($completed_tasks/$TOTAL_TASKS) ; ETC: $estimated_completion_date" 
    
    # Simple ASCII progress bar
    read -r rows cols < <(stty size)
    bar_length=$(( $cols - 2 ))
    filled_length=$(echo "$bar_length*$completed_tasks/$TOTAL_TASKS" | bc)
    printf "["
    printf "%0.s=" $(seq 1 $filled_length)
    printf "%0.s " $(seq 1 $(($bar_length-$filled_length)))
    printf "]\n"
    sleep 10m
    echo
    echo "]]]]]]]]]]]]]]]]]]]][[[[[[[[[[[[[[[[[[[["
    echo
done
