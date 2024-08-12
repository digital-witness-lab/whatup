ARG CONFIGURE_VM_SECRETS_REPO=configure-vm-secrets:latest
ARG LOG_CLEANER_REPO=log-cleaner:latest

FROM $CONFIGURE_VM_SECRETS_REPO AS configure-vm-secrets
FROM $LOG_CLEANER_REPO AS log-cleaner

FROM golang:1.22-bullseye AS whatupcore2

WORKDIR /build

RUN apt update \
    && apt upgrade -y \
    && apt install -y \
    libssl-dev \
    libpcre2-8-0

RUN apt auto-clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

ENV GOCACHE /usr/local/cache/go-build-cache/
ENV GOMODCACHE /usr/local/cache/go-mod-cache/

RUN \
    --mount=type=cache,target=/usr/local/cache/go-build-cache/ \
    --mount=type=cache,target=/usr/local/cache/go-mod-cache/ \
    go mod download

# Ensure the script is executable.
RUN chmod +x /build/run.sh

RUN \
    --mount=type=cache,target=/usr/local/cache/go-build-cache/ \
    --mount=type=cache,target=/usr/local/cache/go-mod-cache/ \
    make whatupcore2

FROM gcr.io/distroless/base-debian11 AS run

WORKDIR /

# Copy shared libraries required by the tools we need to run.
# Use `ldd <absolute path to the program>`.
COPY --from=whatupcore2 /lib/x86_64-linux-gnu/libtinfo.so.6 /lib/x86_64-linux-gnu/libtinfo.so.6
COPY --from=whatupcore2 /lib/x86_64-linux-gnu/libdl.so.2 /lib/x86_64-linux-gnu/libdl.so.2
COPY --from=whatupcore2 /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/libc.so.6
COPY --from=whatupcore2 /lib/x86_64-linux-gnu/libpthread.so.0 /lib/x86_64-linux-gnu/libpthread.so.0
COPY --from=whatupcore2 /lib/x86_64-linux-gnu/libselinux.so.1 /lib/x86_64-linux-gnu/libselinux.so.1
COPY --from=whatupcore2 /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0
COPY --from=whatupcore2 /lib64/ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2

# Copy the tools we need in this final image.
COPY --from=whatupcore2 /bin/bash /bin/bash
COPY --from=whatupcore2 /usr/bin/env /usr/bin/env
COPY --from=whatupcore2 /bin/cat /bin/cat
COPY --from=whatupcore2 /bin/ls /bin/ls

# Finally, copy the app binary and related scripts.
COPY --from=whatupcore2 /build/whatupcore2 /whatupcore2
COPY --from=whatupcore2 /build/run.sh /run.sh

# Copy internal utility programs
COPY --from=configure-vm-secrets /configureVmSecrets /configureVmSecrets
COPY --from=log-cleaner /log-cleaner /log-cleaner

EXPOSE 3447

ARG ENVIRONMENT="dev"
ENV ENVIRONMENT=$ENVIRONMENT

ENTRYPOINT ["/run.sh"]
