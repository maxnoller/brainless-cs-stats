import pika
import requests
import os
import logging
from google.cloud import storage

def on_message_callback(channel, method, properties, body):
    url = body.decode()
    logging.info(f"Received Demo URL: {url}")

connection_params = pika.ConnectionParameters()
    
