#!/bin/env sh

if [ -e /run/secrets/photo-dna-key ]; then
    echo "Setting PHOTO_DNA_KEY from docker secret"
    export PHOTO_DNA_KEY=$( cat /run/secrets/photo-dna-key )
fi

java \
    -XX:+UnlockExperimentalVMOptions \
    -XX:+UseCGroupMemoryLimitForHeap \
    -Djava.security.egd=file:/dev/./urandom \
    -jar /app/photocop.jar \
    $@
