from services.unify_irc import IRC_Session
from services.unify_facebook import Facebook_Session

class Broadcaster:

    def __init__(self, clients={}):
        self.clients = clients

    def add_client(self, client_id, obj):
        self.clients[client_id] = obj

    def mass_broadcast(self, client_id, message, sender=""):
        for client in self.clients:
            if client_id != client:
                client.broadcast(message, sender=sender)

"""
Simple config. Will be changed later
"""

CLIENT_MAP = {
    "irc" : IRC_Session,
    "facebook" : Facebook_Session
}

