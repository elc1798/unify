"""
This bot listens to port 5002 for incoming connections from Facebook. It takes
in any messages that the bot receives and echos it back.
"""
from flask import Flask, request
from pymessenger.bot import Bot

app = Flask(__name__)

ACCESS_TOKEN = "EAAZAfaqKwEYEBAA5Q0Lllc0aFVfp2zvsYgxQoFt8WaPhEDaw3Ohl34oLzZCyR8FQDWZCSIkl2FMPYdQPH7iBDa0QcZA6Hebupe44uKx1E716I9NOciv4xstTucRJe6NU50py5j5fLQAdBfkHvYdWZCB06bQtSeWOADd8l9C3rHQZDZD"
VERIFY_TOKEN = ""
bot = Bot(ACCESS_TOKEN)


@app.route("/", methods=['GET', 'POST'])
def hello():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        else:
            return 'Invalid verification token'

    if request.method == 'POST':
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for x in messaging:
                if x.get('message'):
                    recipient_id = x['sender']['id']
                    if x['message'].get('text'):
                        message = x['message']['text']
                        bot.send_text_message(recipient_id, message)
                    if x['message'].get('attachment'):
                        bot.send_attachment_url(recipient_id, x['message']['attachment']['type'],
                                                x['message']['attachment']['payload']['url'])
                else:
                    pass
        return "Success"


if __name__ == "__main__":
    app.run(port=5002, debug=True)