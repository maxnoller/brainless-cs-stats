import pika
import requests
import os
import logging
from google.cloud import storage

AMQP_URL = os.environ.get('AMQP_URL')
BUCKET_NAME = os.environ.get("BUCKET_NAME")


def download_file(url):
    response = requests.get(url, stream=True)
    return response.content

def upload_to_gcs(data, bucket_name, prefix):
    filename = f"{prefix}/{int(time.time())}" if prefix else int(time.time())
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(data)
    logging.info(f"File uploaded to {destination_blob_name}")

def callback(channel, method, properties, body):
    logging.info(f"Received request to download {body}")
    demo_url = json.loads(body)["url"]
    demo_data = download_file(demo_url)
    upload_to_gcs(demo_data, bucket_name) 

connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))    
channel = connection.channel()

channel.queue_declare(queue="demo_urls")
channel.basic_consume(queue="demo_urls", on_message_callback=on_message_callback, auto_ack=True)

logging.info(f"Waiting for messages.")
channel.start_consuming()
