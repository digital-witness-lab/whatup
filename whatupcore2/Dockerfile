FROM golang:1.20-bullseye AS builder

WORKDIR /build

RUN apt update \
    && apt upgrade -y \
    && apt install -y \
    libsqlite3-0 \
    libsqlite3-dev \
    libsqlcipher0 \
    libsqlcipher-dev \
    libssl-dev \
    && apt auto-clean \
    && rm -rf /var/lib/apt/lists/*

# Install gcsfuse and its dependencies.
# https://cloud.google.com/run/docs/tutorials/network-filesystems-fuse#defining_your_environment_configuration_with_the_dockerfile
RUN apt install -y \
    curl \
    gnupg \
    lsb-release \
    tini && \
    gcsFuseRepo=gcsfuse-`lsb_release -c -s` && \
    echo "deb http://packages.cloud.google.com/apt $gcsFuseRepo main" | \
    tee /etc/apt/sources.list.d/gcsfuse.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key add - && \
    apt update && \
    apt install -y gcsfuse && \
    apt clean

COPY go.mod go.sum ./
COPY protos/ ./

# Ensure the script is executable.
RUN chmod +x /build/gcsfuse_run.sh

RUN go mod download

ENV GOCACHE /usr/local/cache/go-build-cache/
ENV GOMODCACHE /usr/local/cache/go-mod-cache/

COPY . .
RUN \
    --mount=type=cache,target=/usr/local/cache/go-build-cache/ \
    --mount=type=cache,target=/usr/local/cache/go-mod-cache/ \
    make whatupcore2

FROM gcr.io/distroless/base-debian11 AS run
WORKDIR /

COPY --from=builder /build/whatupcore2 /whatupcore2
COPY --from=builder /build/gcsfuse_run.sh /gcsfuse_run.sh

EXPOSE 3447

# Use tini to manage zombie processes and signal forwarding.
# https://github.com/krallin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

# Pass the wrapper script as arguments to tini.
CMD ["/app/gcsfuse_run.sh"]
