function find-message() {
    id=$1
    find data/message-archive/ -type f -name \*${id}.json
}

function message-json() {
    id=$1
    find data/message-archive/ -type f -name \*${id}.json -exec jq '.' \;
}
