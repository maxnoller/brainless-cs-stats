import gevent.monkey
gevent.monkey.patch_all()
from google.protobuf.message import Message
from pika.adapters.gevent_connection import GeventConnection
from steam.client import SteamClient
from steam.guard import SteamAuthenticator
from csgo.client import CSGOClient
from google.protobuf.json_format import MessageToJson
from csgo import sharecode
import json
import os
import logging
import pika
import gevent
from gevent.event import AsyncResult
logging.basicConfig(level=logging.INFO)

client = SteamClient()
cs = CSGOClient(client)

def getSharecodeInfo(matchcode: str):
    info = sharecode.decode(matchcode)
    return info

@client.on('logged_on')
def start_csgo():
    print("logged on")
    cs.launch()

@cs.on('ready')
def gc_ready():
    print("[CS-GO] info: %s" % cs.ready)

@client.on('disconnected')
def handle_disconnect():
    print("Disconnected from Steam.")
    reconnect()

def reconnect(attempts=0):
    max_retries = 5  # Set a max number of retries
    wait_time = min(2 ** attempts, 60)  # Exponential backoff, max wait is 60 seconds

    if attempts < max_retries:
        print(f"Attempting to reconnect in {wait_time} seconds...")
        time.sleep(wait_time)  # Wait before reconnecting
        try:
            client.reconnect(maxdelay=30)  # Attempt to reconnect
        except Exception as e:
            print(f"Reconnect failed: {e}")
            reconnect(attempts + 1)
    else:
        print("Max reconnection attempts reached. Exiting.")
        # Handle max retries reached (e.g., exit or alert the user)

def fetch_match_info(demo_code):
    Sharecode = getSharecodeInfo(demo_code)
    cs.request_full_match_info(matchid=Sharecode['matchid'], outcomeid=Sharecode['outcomeid'], token=Sharecode['token'])

    # Create an AsyncResult object
    result = AsyncResult()

    # Define a callback function that will be called when the event is received
    def on_full_match_info(event, response):
        result.set(MessageToJson(response))

    # Register the callback with the event
    cs.on('full_match_info', on_full_match_info)

    # Wait for the result in a non-blocking way
    response_json = result.get(timeout=30)  # Set an appropriate timeout
    cs.remove_event_handler('full_match_info', on_full_match_info)

    return response_json

def demo_callback(ch, method, properties, body):
    print(f" [x] received {body}")

LOGGER = logging.getLogger(__name__)

AMQP_URL = os.getenv("AMQP_URL")
QUEUE = "demo_codes"

def on_connection_open(connection):
    LOGGER.info('Connection opened')
    open_channel(connection)


def open_channel(connection):
    connection.channel(on_open_callback=on_channel_open)


def on_channel_open(channel):
    LOGGER.info('Channel opened')
    setup_queue(channel)


def setup_queue(channel):
    LOGGER.info('Declaring queue %s', QUEUE)
    channel.queue_declare(queue=QUEUE, durable=True, callback=lambda frame: on_queue_declareok(channel))
    channel.queue_declare(queue="demo_urls", durable=True)


def on_queue_declareok(channel):
    LOGGER.info('Queue declared')
    start_consuming(channel)


def start_consuming(channel):
    LOGGER.info('Starting consumer')
    channel.basic_consume(QUEUE, on_message)


def on_message(channel, method, properties, body):
    LOGGER.info('Received message: %s', body)
    channel.basic_ack(method.delivery_tag)
    data = fetch_match_info(body.decode("utf-8"))
    LOGGER.info(data)

def run():
    connection = GeventConnection(
        parameters=pika.URLParameters(AMQP_URL),
        on_open_callback=on_connection_open)

    gevent.spawn(connection.ioloop.start())
    return connection


def stop(connection):
    if connection and connection.is_open:
        LOGGER.info('Closing connection')
        connection.close()


def main():
    connection = run()
    try:
        gevent.wait()
    except KeyboardInterrupt:
        stop(connection)


if __name__ == '__main__':
    secrets = json.loads(os.getenv("STEAM_2FA"))
    sa = SteamAuthenticator(secrets)
    client.login(username=os.getenv("STEAM_USER"), password=os.getenv("STEAM_PASSWORD"), two_factor_code=sa.get_code())
    main() 
