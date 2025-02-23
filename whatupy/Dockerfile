ARG CONFIGURE_VM_SECRETS_REPO=configure-vm-secrets:latest
ARG LOG_CLEANER_REPO=log-cleaner:latest

FROM $CONFIGURE_VM_SECRETS_REPO as configure-vm-secrets
FROM $LOG_CLEANER_REPO as log-cleaner

FROM python:3.11-slim-bullseye

WORKDIR /usr/src/whatupy

RUN apt update && apt upgrade -y && \
    apt install -y wamerican-large && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/share/dict/american-english-large /usr/share/dict/words

RUN mkdir /usr/src/whatupy-data/

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
