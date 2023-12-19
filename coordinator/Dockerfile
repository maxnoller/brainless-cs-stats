FROM python:3.8-slim-buster

WORKDIR /app

COPY coordinator/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./coordinator/. .

CMD [ "python3", "./coordinator.py"]
