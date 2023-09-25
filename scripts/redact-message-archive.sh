#!/bin/bash
#
# This script will take in a message archive and mirror it into a new archive
# that has been run through `whatupcore2 redact`. It uses parallel to run and
# keeps a joblog. In case of failures, you can re-run only failed redactions
# using:
# 
# parallel --retry-failed --joblog ./<new-archive>/job.log

redact_cmd="docker compose run -T whatup redact -"
redact_string_cmd="docker compose run -T whatup redact-string "
source_archive=$1
target_archive=$2
message_type=

find_groupinfo='group-info_[0-9]+.json'
find_wumessage='[0-9]+_[A-Z0-9]+\.json$'
find_media='/media$'
find_deanon_dir='[0-9]{4,}@s.whatsapp.net'

log_success=$target_archive/redact.success.log
log_fail=$target_archive/redact.fail.log

function clean-path() {
    IFS='/' read -ra path <<< "$1";
    first=true
    for comp in "${path[@]}"; do
        if [ "$first" != true ]; then
            echo -n '/'
        fi
        if [[ "$comp" =~ $find_deanon_dir ]]; then 
            $redact_string_cmd ${comp%@*} ; echo -n "@s.whatsapp.net"
        else
            echo -n $comp
        fi
        first=false
    done
}

(
for source in $( find "$source_archive" -type f -name \*.json -or -type d -name media ) ; do
    source_clean=$( clean-path $source )
    target_rel=$( realpath --relative-to="$source_archive" "$source_clean" )
    target_parent=$target_archive/$( dirname "$target_rel" )
    target=$target_archive/$target_rel

    if [[ "$source" =~ $find_groupinfo ]]; then
        message_type="GroupInfo"
    elif [[ "$source" =~ $find_wumessage ]]; then
        message_type="WUMessage"
    elif [[ "$source" =~ $find_media ]]; then
        echo -en "cp -r $source $target\0"
        continue
    else
        # This will fail and will continue to fail if retrying through parallel's joblog.
        message_type="XXXX"
    fi
    mkdir -p "${target_parent}"
    echo -en "cat $source | $redact_cmd > $target\0"
done;
) | parallel --jobs "200%" --bar --null --joblog $target_archive/job.log
