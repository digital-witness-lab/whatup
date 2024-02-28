ARG CONFIGURE_VM_SECRETS_REPO=configure-vm-secrets:latest
FROM $CONFIGURE_VM_SECRETS_REPO as configure-vm-secrets

FROM python:3.11-slim-bullseye

COPY --from=configure-vm-secrets /configureVmSecrets /configureVmSecrets

WORKDIR /usr/src/whatupy

RUN --mount=type=cache,target=/var/lib/apt/lists/ \
    apt update && apt upgrade -y && \
    apt install -y curl && \
    apt autoremove -y

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

LABEL org.digitalwitnesslab.project="whatup"
LABEL org.digitalwitnesslab.module="whatupy"
HEALTHCHECK --interval=5s --timeout=5s --start-period=20s CMD ["true"]

ARG ENVIRONMENT="dev"
ENV ENVIRONMENT=$ENVIRONMENT
