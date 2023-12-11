FROM python:3.11-slim-bullseye

WORKDIR /usr/src/hash-generator

RUN apt update && apt upgrade -y && apt install -y curl

COPY requirements.txt .
RUN pip install -r requirements.txt

# copied parts of the whatupy dockerfile, not sure if this works