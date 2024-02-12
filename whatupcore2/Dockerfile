# Note: This Dockerfile is executed with the root of
# the repo as the context since it relies on
# configure-vm-secrets.

FROM golang:1.20-bullseye AS whatupcore2

WORKDIR /build

RUN apt update \
    && apt upgrade -y \
    && apt install -y \
    libssl-dev \
    libpcre2-8-0

RUN apt auto-clean && \
    rm -rf /var/lib/apt/lists/*

COPY whatupcore2/ ./

RUN go mod download

ENV GOCACHE /usr/local/cache/go-build-cache/
ENV GOMODCACHE /usr/local/cache/go-mod-cache/

# Ensure the script is executable.
RUN chmod +x /build/run.sh

RUN \
    --mount=type=cache,target=/usr/local/cache/go-build-cache/ \
    --mount=type=cache,target=/usr/local/cache/go-mod-cache/ \
    make whatupcore2

FROM golang:1.20-bullseye AS configure-vm-secrets

WORKDIR /build

COPY configure-vm-secrets/. .

RUN go mod download

RUN make build

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

# Finally, copy the app binary and related scripts.
COPY --from=whatupcore2 /build/whatupcore2 /whatupcore2
COPY --from=whatupcore2 /build/run.sh /run.sh

COPY --from=configure-vm-secrets /build/configureVmSecrets /configureVmSecrets

EXPOSE 3447

ARG ENVIRONMENT="dev"
ENV ENVIRONMENT=$ENVIRONMENT

ENTRYPOINT ["/run.sh"]
