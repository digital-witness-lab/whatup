FROM golang:1.20-bullseye AS builder

WORKDIR /build

COPY . .

ENV GOCACHE /usr/local/cache/go-build-cache/
ENV GOMODCACHE /usr/local/cache/go-mod-cache/

RUN \
    --mount=type=cache,target=/usr/local/cache/go-build-cache/ \
    --mount=type=cache,target=/usr/local/cache/go-mod-cache/ \
    go mod download

RUN \
    --mount=type=cache,target=/usr/local/cache/go-build-cache/ \
    --mount=type=cache,target=/usr/local/cache/go-mod-cache/ \
    make build


FROM gcr.io/distroless/base-debian11 AS run
COPY --from=builder /build/log-cleaner /log-cleaner
