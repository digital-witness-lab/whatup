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
    libpcre2-8-0

RUN apt auto-clean && \
    rm -rf /var/lib/apt/lists/*

COPY go.mod go.sum ./
COPY protos/ ./

RUN go mod download

ENV GOCACHE /usr/local/cache/go-build-cache/
ENV GOMODCACHE /usr/local/cache/go-mod-cache/

COPY . .

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
COPY --from=builder /lib/x86_64-linux-gnu/libtinfo.so.6 /lib/x86_64-linux-gnu/libtinfo.so.6
COPY --from=builder /lib/x86_64-linux-gnu/libdl.so.2 /lib/x86_64-linux-gnu/libdl.so.2
COPY --from=builder /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/libc.so.6
COPY --from=builder /lib/x86_64-linux-gnu/libpthread.so.0 /lib/x86_64-linux-gnu/libpthread.so.0
COPY --from=builder /lib/x86_64-linux-gnu/libselinux.so.1 /lib/x86_64-linux-gnu/libselinux.so.1
COPY --from=builder /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0
COPY --from=builder /lib64/ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2

# Copy the tools we need in this final image.
COPY --from=builder /bin/bash /bin/bash
COPY --from=builder /usr/bin/env /usr/bin/env
COPY --from=builder /bin/mkdir /bin/mkdir

# Finally, copy the app binary and related scripts.
COPY --from=builder /build/whatupcore2 /whatupcore2
COPY --from=builder /build/run.sh /run.sh

EXPOSE 3447

ENTRYPOINT ["/run.sh"]
