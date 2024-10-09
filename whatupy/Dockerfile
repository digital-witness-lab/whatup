ARG CONFIGURE_VM_SECRETS_REPO=configure-vm-secrets:latest
ARG LOG_CLEANER_REPO=log-cleaner:latest

FROM $CONFIGURE_VM_SECRETS_REPO AS configure-vm-secrets
FROM $LOG_CLEANER_REPO AS log-cleaner

FROM python:3.11-slim-bullseye

WORKDIR /usr/src/whatupy

RUN apt update && apt upgrade -y && \
    apt install -y curl && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/share/dict/ && \
    curl -o /usr/share/dict/words "https://svnweb.freebsd.org/base/head/share/dict/web2?revision=326913&view=co&pathrev=326913" && \
    mkdir /usr/src/whatupy-data/

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -e .

# Ensure the script is executable.
RUN chmod +x /usr/src/whatupy/*.sh

COPY --from=configure-vm-secrets /configureVmSecrets /configureVmSecrets
COPY --from=log-cleaner /log-cleaner /log-cleaner

ARG ENVIRONMENT="dev"
ENV ENVIRONMENT=$ENVIRONMENT
