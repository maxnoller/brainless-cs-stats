FROM python:3.8-slim-buster

WORKDIR /usr/var/app

COPY demo-fetcher/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./demo-fetcher/ .

CMD [ "python3", "demo-fetch-server.py"]
