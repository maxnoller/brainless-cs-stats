FROM python:3-slim-buster

WORKDIR /app

ADD ./download-service/. /app

RUN pip install -r requirements.txt

EXPOSE 80

CMD ["python", "download_service.py"]
