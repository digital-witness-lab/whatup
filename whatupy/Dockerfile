FROM python:3.11-alpine

WORKDIR /usr/src/whatupy

COPY requirements.txt .
RUN pip install -r requirements.txt ; mkdir /usr/src/whatupy-data/

COPY . .
RUN pip install .
