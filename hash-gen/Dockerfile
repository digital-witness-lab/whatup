FROM python:3.11-slim-bullseye

WORKDIR /usr/src/hash-gen/

COPY run.sh .
RUN chmod +x run.sh

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

ENTRYPOINT ["/usr/src/hash-gen/run.sh"]
