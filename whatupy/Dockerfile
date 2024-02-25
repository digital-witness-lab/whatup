ARG CONFIGURE_VM_SECRETS_REPO=configure-vm-secrets:latest
FROM $CONFIGURE_VM_SECRETS_REPO as configure-vm-secrets

FROM python:3.11-slim-bullseye

COPY --from=configure-vm-secrets /configureVmSecrets /configureVmSecrets

WORKDIR /usr/src/whatupy

RUN apt update && apt upgrade -y && apt install -y curl

RUN mkdir -p /usr/share/dict/ && \
    curl -o /usr/share/dict/words "https://svnweb.freebsd.org/base/head/share/dict/web2?revision=326913&view=co&pathrev=326913"

COPY requirements.txt .
RUN pip install -r requirements.txt ; mkdir /usr/src/whatupy-data/

COPY . .
RUN pip install -e .

# Ensure the script is executable.
RUN chmod +x /usr/src/whatupy/*.sh

ARG ENVIRONMENT="dev"
ENV ENVIRONMENT=$ENVIRONMENT
