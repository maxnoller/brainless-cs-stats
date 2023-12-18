FROM python:3.8-slim-buster

WORKDIR /app

COPY demo-fetcher/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./demo-fetcher/. .

CMD [ "python3", "/app/demo-fetch-server.py"]
