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
logging.basicConfig(level=logging.DEBUG)

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

def fetch_match_info(demo_code):
    Sharecode = getSharecodeInfo(demo_code)
    cs.request_full_match_info(matchid=Sharecode['matchid'], outcomeid=Sharecode['outcomeid'], token=Sharecode['token'])
    response, = cs.wait_event('full_match_info')
    print("[CS-GO] response: %s" % response)
    return response

#@app.route('/submit_demo', methods=['POST'])
#def submit_demo():
#    demo_code = request.get_json()['demo_code']
#    match_info = fetch_match_info(demo_code)
#    return jsonify(MessageToJson(match_info))

def demo_callback(ch, method, properties, body):
    print(f" [x] received {body}")

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

AMQP_URL = os.getenv("AMQP_URL")
QUEUE = "demo_urls"

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
    channel.queue_declare(queue=QUEUE, callback=lambda frame: on_queue_declareok(channel))


def on_queue_declareok(channel):
    LOGGER.info('Queue declared')
    start_consuming(channel)


def start_consuming(channel):
    LOGGER.info('Starting consumer')
    channel.basic_consume(QUEUE, on_message)


def on_message(channel, method, properties, body):
    LOGGER.info('Received message: %s', body)
    channel.basic_ack(method.delivery_tag)


def run():
    connection = GeventConnection(
        parameters=pika.URLParameters(AMQP_URL),
        on_open_callback=on_connection_open,
        connection_class=GeventConnection,
        custom_ioloop=gevent.get_hub().loop)

    gevent.spawn(connection.ioloop.start)
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
