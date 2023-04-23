FROM python:3.10-slim

COPY requirements.txt /
RUN pip3 install -r requirements.txt

COPY ./src ./src
ENTRYPOINT python3 src/main.py