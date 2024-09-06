FROM python:3.12

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -e .

ARG ENVIRONMENT="dev"
ENV ENVIRONMENT=$ENVIRONMENT
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["diwi-api"]
