import socket, asyncore, asynchat
import hashlib, random
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

class IRC_Session(asynchat.async_chat):

    def __init__(self, debug=False, controller=None):
        """
        IRC Session initializer. Creates an internal variable for:
            input_buffer    (str)
            debug           (bool)
            dispatch        (list)
            msgstack        (list)
            logged_in       (bool)

        The 'recv' terminator is also set to a 'Windows' Style newline
        """
        asynchat.async_chat.__init__(self)
        self.input_buffer = ''
        self.set_terminator('\r\n')
        self.debug = debug
        self.controller = controller

        self.dispatch = []
        self.msgstack = []
        self.logged_in = False

    def send_irc(self, args, *text):
        """
        Constructs an IRC compliant command
        """
        command = ' '.join(args)
        if text:
            command = command + " :" + ' '.join(text)
        self.push(command + '\r\n')
        if self.debug:
            print "[SENT] %s" % (command,)

    def handle_connect(self):
        """
        Python asyncore function:

        Is run when a connection is established via a socket.

        Will set the NICK and USERNAME of bot upon connection
        """
        if self.debug:
            print "Connection established."
        self.send_irc(['NICK', config.USERNAME])
        self.send_irc(['USER', config.USERNAME, '8', '*'], config.USERNAME)

    def collect_incoming_data(self, bytes):
        """
        Python asynchat function

        Will aggregate data to be put into our input buffer
        """
        self.input_buffer += bytes

    def found_terminator(self):
        line = self.input_buffer
        self.input_buffer = ""

        if self.debug:
            print "[RECV] %s" % (line,)

        # IMPORTANT!
        sep = line.split(" :")
        if len(sep) >= 2 and sep[0] == "PING":
            self.send_irc(['PONG'], " :".join(sep[1:]))

        if not self.logged_in:
            if "This nickname is registered" in line:
                self.send_irc(["PRIVMSG", "NickServ"], "IDENTIFY", config.PASSWORD)
                self.send_irc(['JOIN'], config.CHANNEL)
            if "You are now identified" in line:
                self.logged_in = True
                print "Logged on!"
        else:
            msg = line.split("PRIVMSG %s :" % (config.CHANNEL,))
            if len(line) > 0 and line[0] == ":" and len(msg) >= 2:
                sender = "<irc> " + msg[0].split("!")[0][1:]
                contents = "PRIVMSG %s :" % (config.CHANNEL,)
                contents = contents.join(msg[1:])
                if self.debug:
                    print "[CHAT] %s : %s" % (sender, contents)
                if self.controller is not None:
                    self.controller.mass_broadcast(
                        "irc",
                        contents,
                        sender=sender
                    )
            else:
                if not self.debug:
                    print "[RECV] %s" % (line,)

            # self.broadcast(t, sender="hukara")

    def broadcast(self, message, sender=""):
        contents = "%s >>> %s" % (sender, message)
        self.send_irc(["PRIVMSG", config.CHANNEL], contents)

    def run(self):
        """
        Function to create a socket and begin connection
        """
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.debug:
            print "Connecting to %s:%s" % (config.HOST, config.PORT)
        self.connect( (config.HOST, config.PORT) )
        self.input_buffer = ''
        asyncore.loop()

if __name__ == "__main__":
    bot = IRC_Session(debug=True)
    bot.run()

