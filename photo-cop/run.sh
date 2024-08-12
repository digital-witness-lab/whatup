#!/bin/env sh

if [ -e /run/secrets/photo-cop-key ]; then
    echo "Setting PHOTO_COP_KEY from docker secret"
    export PHOTO_COP_KEY=$( cat /run/secrets/photo-cop-key )
fi

java \
    -XX:+UnlockExperimentalVMOptions \
    -XX:+UseCGroupMemoryLimitForHeap \
    -Djava.security.egd=file:/dev/./urandom \
    -jar /app/photocop.jar \
    $@
