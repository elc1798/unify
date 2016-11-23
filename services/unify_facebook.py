import time, os, sys, threading
import urllib2, requests, json

SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_PARENT_DIR = os.path.dirname(SCRIPT_PATH)
DIR_LEVELS = SCRIPT_PARENT_DIR.split(os.sep)

# Sanity check: We should be in the 'services' directory
assert(DIR_LEVELS[-1] == "services")

# Add the config directory to the sys.path so we can import the IRC config
DIR_LEVELS[-1] = "config"
sys.path.append(os.sep.join(DIR_LEVELS))

import config_facebook as config
import AESCipher

class Facebook_Session():

    def __init__(self, debug=False, controller=None):
        """
        Facebook Session initializer. Creates an internal variable for:
            input_buffer    (str)
            debug           (bool)
            dispatch        (list)
            msgstack        (list)
            logged_in       (bool)

        The 'recv' terminator is also set to a 'Windows' Style newline
        """
        self.enkryptor = AESCipher.AESCipher(config.KRYPT_KEY)
        self.debug = debug
        self.controller = controller

    def run(self):
        while True:
            req = urllib2.Request(config.HOST + "/retrieve")
            response = urllib2.urlopen(req)
            contents = response.read()

            for line in contents.split("\n"):

                if len(line.strip()) == 0:
                    continue

                if self.debug:
                    print "[RECV] %s" % (line,)

                msg = self.enkryptor.decrypt(line).split(" >>> ")
                if len(msg) < 3:
                    print " >>> ".join(msg)
                else:
                    if msg[0] != config.AUTH_KEY:
                        print "[WARN] INVALID AUTH_KEY"
                        return

                    sender = "<Facebook> " + msg[1]
                    contents = " >>> ".join(msg[2:])
                    if self.debug:
                        print "[CHAT] %s : %s" % (sender, contents)
                    if self.controller is not None:
                        self.controller.mass_broadcast(
                            "facebook",
                            contents,
                            sender=sender
                        )
            time.sleep(0.5)

    def broadcast(self, message, sender=""):
        if self.debug:
            print "[SENT] %s" % (message,)

        contents = "%s >>> %s >>> %s" % (config.AUTH_KEY, sender, message)
        contents = self.enkryptor.encrypt(contents)
        headers = {'content-type': 'application/json'}

        r = requests.post(config.HOST + "/send/", data=json.dumps( {'s':
            contents}), headers=headers)

        response = r.content
        if self.debug:
            print response
        if "ok" not in response:
            print "[WARN] Send error"

if __name__ == "__main__":
    bot = Facebook_Session(debug=True)
    recieve_thread = threading.Thread(target=bot.run)
    recieve_thread.daemon = True
    recieve_thread.start()

    while True:
        a = str(raw_input("$> "))
        bot.broadcast(a, sender="tester")

