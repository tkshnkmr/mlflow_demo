FROM python:3.10-slim

COPY requirements.txt /
RUN pip3 install -r requirements.txt

WORKDIR /app

RUN groupadd -r my_user && useradd -g my_user my_user
RUN chown -R my_user:my_user /app
USER my_user

COPY . /app
ENTRYPOINT python3 src/main.py