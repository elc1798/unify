import time, os, sys
import threading

SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_PARENT_DIR = os.path.dirname(SCRIPT_PATH)

sys.path.append(os.sep.join( (SCRIPT_PARENT_DIR, 'services') ))

from unify_irc import IRC_Session
from unify_facebook import Facebook_Session

class Broadcaster:

    def __init__(self, clients={}):
        self.clients = clients
        self.started = False

    def add_client(self, client_id, obj):
        self.clients[client_id] = obj

    def start(self):
        if not self.started:
            self.started = True
            for client in self.clients:
                t = threading.Thread(target=self.clients[client].run)
                t.daemon = True
                t.start()

    def mass_broadcast(self, client_id, message, sender=""):
        for client in self.clients:
            if client_id != client:
                self.clients[client].broadcast(message, sender=sender)

"""
Simple config. Will be changed later
"""

CLIENT_MAP = {
    "irc" : IRC_Session,
    "facebook" : Facebook_Session
}

if __name__ == "__main__":
    main_broadcaster = Broadcaster()
    for client in CLIENT_MAP:
        main_broadcaster.add_client(
            client,
            CLIENT_MAP[client](
                debug=True,
                controller=main_broadcaster
            )
        )

    # Start running all the clients:
    main_broadcaster.start()

    # When do we quit?
    s = ""
    while s != "stop":
        s = str(raw_input("Enter 'stop' to stop: "))

    sys.exit(0)

