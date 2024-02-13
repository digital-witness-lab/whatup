# Note: This Dockerfile is executed with the root of
# the repo as the context since it relies on
# configure-vm-secrets.

FROM golang:1.20-bullseye AS configure-vm-secrets

WORKDIR /build

COPY configure-vm-secrets/. .

RUN go mod download

RUN make build

FROM python:3.11-slim-bullseye

WORKDIR /

COPY --from=configure-vm-secrets /build/configureVmSecrets /configureVmSecrets

WORKDIR /usr/src/whatupy

RUN apt update && apt upgrade -y && apt install -y curl

RUN mkdir -p /usr/share/dict/ && \
    curl -o /usr/share/dict/words "https://svnweb.freebsd.org/base/head/share/dict/web2?revision=326913&view=co&pathrev=326913"

COPY whatupy/requirements.txt .
RUN pip install -r requirements.txt ; mkdir /usr/src/whatupy-data/

COPY whatupy/ .
RUN pip install -e .

# Ensure the script is executable.
RUN chmod +x /usr/src/whatupy/*.sh

ARG ENVIRONMENT="dev"
ENV ENVIRONMENT=$ENVIRONMENT
