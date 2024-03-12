FROM python:3.11-slim-bullseye

WORKDIR /usr/src/hash-gen/

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -e .
RUN chmod +x run.sh

ENTRYPOINT ["/usr/src/hash-gen/run.sh"]
