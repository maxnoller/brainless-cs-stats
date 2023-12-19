from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from steam.client import SteamClient
from steam.guard import SteamAuthenticator
from csgo.client import CSGOClient
from google.protobuf.json_format import MessageToJson
from csgo import sharecode
import json
import os
import logging
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

app = Flask(__name__)
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

@app.route('/submit_demo', methods=['POST'])
def submit_demo():
    demo_code = request.get_json()['demo_code']
    match_info = fetch_match_info(demo_code)
    return jsonify(MessageToJson(match_info))

if __name__ == "__main__":
    print("Logged in")
    secrets = json.loads(os.getenv("STEAM_2FA"))
    sa = SteamAuthenticator(secrets)
    client.login(username=os.getenv("STEAM_USER"), password=os.getenv("STEAM_PASSWORD"), two_factor_code=sa.get_code())
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
