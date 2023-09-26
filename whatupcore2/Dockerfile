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

COPY go.mod go.sum ./
COPY protos/ ./

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

EXPOSE 3447

ENTRYPOINT ["/whatupcore2"]
CMD ["rpc", "--log-level=INFO"]
