import os, asyncore
import sys
import json

import requests
from flask import Flask, request

import socket, asyncore
import AESCipher

app = Flask(__name__)

known_recipients = []

AUTH_KEY = "<AUTH_KEY_HERE>"
KRYPT_KEY = "<AES KEY HERE>"

enkryptor = AESCipher.AESCipher(KRYPT_KEY)
msg_queue = []

@app.route('/send', methods=['POST'])
@app.route('/send/', methods=['POST'])
def send_to_fb():
    global enkryptor
    global AUTH_KEY

    data = request.get_json()

    if data is None or 's' not in data:
        return "no data", 200

    data = data['s']

    log(data)
    dekrypted = enkryptor.decrypt(data)
    log(dekrypted)
    msg = dekrypted.split(" >>> ")

    if len(msg) < 3 or msg[0] != AUTH_KEY:
        return "bad", 403

    contents = " >>> ".join(msg[1:])
    for rec in known_recipients:
        send_message(rec, contents)

    return "ok", 200

@app.route('/retrieve')
@app.route('/retrieve/')
def retrieve():
    global msg_queue
    retval = "\n".join(msg_queue)
    msg_queue[:] = []
    return retval, 200

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200

@app.route('/', methods=['POST'])
def webhook():
    global known_recipients
    global msg_queue
    global enkryptor

    data = request.get_json()
    log(data)

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):

                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"]["id"]
                    message_text = messaging_event["message"]["text"]

                    if sender_id not in known_recipients:
                        known_recipients.append(sender_id)

                    contents = enkryptor.encrypt("%s >>> %s >>> %s" % (AUTH_KEY,
                        get_name_from_id(sender_id), message_text))

                    msg_queue.append(contents)

                if messaging_event.get("delivery"):
                    pass
                if messaging_event.get("optin"):
                    pass
                if messaging_event.get("postback"):
                    pass

    return "ok", 200

id_name_map = {}

def get_name_from_id(mess_id):
    global id_name_map
    if mess_id in id_name_map:
        return id_name_map[mess_id]

    url = "https://graph.facebook.com/v2.6/%s?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=%s"
    r = requests.get(url % (mess_id, os.environ["PAGE_ACCESS_TOKEN"]))
    resp = r.json()
    name = mess_id
    if "first_name" in resp:
        name = resp["first_name"]
        if "last_name" in resp:
            name += " %s" % (resp["last_name"],)
    id_name_map[mess_id] = name
    return name

def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    log("Starting Flask application...")
    app.run(debug=True)

