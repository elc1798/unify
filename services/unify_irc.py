import socket, urllib2
import string, random
import hashlib
import time, os, sys

SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_PARENT_DIR = os.path.dirname(SCRIPT_PATH)
DIR_LEVELS = SCRIPT_PARENT_DIR.split(os.sep)

# Sanity check: We should be in the 'services' directory
assert(DIR_LEVELS[-1] == "services")

# Add the config directory to the sys.path so we can import the IRC config
DIR_LEVELS[-1] = "config"
sys.path.append(os.sep.join(DIR_LEVELS))

import config_irc as config

class IRC_Session:

    def __init__(self, debug=False):
        self.s = None
        self.connected = False
        self.debug = debug

    def connect(self):
        if self.connected:
            return

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect( (config.HOST, config.PORT ))

        self.s.send("NICK %s\r\n" % (config.USERNAME,))
        self.s.send("USER %s 8 * :%s\r\n" % (config.USERNAME, config.USERNAME))

        ping_pong = self.s.recv(512)
        print "PING RECEIVED: ", repr(ping_pong)
        ping_pong = ping_pong[5:]
        print "PONT SENT: ", 'PONG %s\r\n' % (ping_pong,)
        self.s.send('PONG %s\r\n' % (ping_pong,))

        wait_for_login = self.s.recv(512)
        while "identify" not in wait_for_login:
            wait_for_login = self.s.recv(512)
            if self.debug:
                print wait_for_login

        self.s.send("JOIN %s\r\n" % (config.CHANNEL,))
        self.s.send(config.LOGIN_MSG)

        wait_for_auth = self.s.recv(512)
        while "End of /NAMES list." not in wait_for_auth:
            wait_for_auth = self.s.recv(512)
            if self.debug:
                print wait_for_auth

        print "Log on successful"
        self.connected = True

    def recv(self):
        if not self.connected:
            return

        msg = self.s.recv(512).split(":")
        assert(len(msg) == 3)

        sender = msg[1].split("!")[0]
        contents = msg[2]
        return (sender, contents)

    def send(self, message):
        if not self.connected:
            return

        self.s.send("PRIVMSG %s :%s\r\n" % (config.CHANNEL, message))

if __name__ == "__main__":
    sess = IRC_Session(debug=True)
    sess.connect()
    while True:
        sess.recv()

