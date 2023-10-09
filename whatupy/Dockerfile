FROM python:3.11

WORKDIR /usr/src/whatupy

RUN mkdir -p /usr/share/dict/ && \
    wget -O /usr/share/dict/words "https://svnweb.freebsd.org/base/head/share/dict/web2?revision=326913&view=co&pathrev=326913"

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

COPY requirements.txt .
RUN pip install -r requirements.txt ; mkdir /usr/src/whatupy-data/

COPY . .
RUN pip install -e .

# Ensure the script is executable.
RUN chmod +x /usr/src/whatupy/*.sh

# Use tini to manage zombie processes and signal forwarding.
# https://github.com/krallin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]
