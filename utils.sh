function find-message() {
    id=$1
    find data/message-archive/ -type f -name \*${id}.json
}

function message-json() {
    id=$1
    find data/message-archive/ -type f -name \*${id}.json -exec jq '.' \;
}

function message-recent() {
    find data/message-archive/ -type f -printf "%T@ %p\n" | sort -n | cut -d' ' -f 2- | tail -n 1 | xargs jq '.'
}
