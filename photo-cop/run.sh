#!/bin/env sh

# Run the VM secrets configurator.
# If we are not running inside a VM,
# it will exit silently.
/configureVmSecrets
if [ -e /tmp/whatup/.env ]; then
    set -o allexport
    source /tmp/whatup/.env 
    set +o allexport
fi

if [ -e /run/secrets/photo-dna-key ]; then
    echo "Setting PHOTO_DNA_KEY from docker secret"
    export PHOTO_DNA_KEY=$( cat /run/secrets/photo-dna-key )
fi

exec /log-cleaner java \
    -XX:+UnlockExperimentalVMOptions \
    -XX:+UseCGroupMemoryLimitForHeap \
    -Djava.security.egd=file:/dev/./urandom \
    -jar /app/photocop.jar \
    $@
