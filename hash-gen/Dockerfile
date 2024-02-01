FROM python:3.11-slim-bullseye

WORKDIR /usr/src/hash-generator

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

# ENTRYPOINT ["hash-gen"]