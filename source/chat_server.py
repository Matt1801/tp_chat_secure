import logging
import sys

from Pyro5.api import Daemon, expose
from Pyro5.errors import ConnectionClosedError
from Pyro5.server import behavior

# https://github.com/irmen/Pyro5/blob/master/examples/callback/server2.py


@behavior("single")
class ChatServer(object):
    def __init__(self):
        self._buffer = dict()
        self._log = logging.getLogger(self.__class__.__name__)

    @expose
    def register(self, user, callback):
        self._buffer[user] = callback
        self._log.info(f"Register a new user {user} with callback handler {callback}")
        self._log.debug(f"User list : {list(self._buffer)}")

    @expose
    def send_message(self, user, message):
        self._log.info(f"{user} send message : {message}")
        for register_user in list(self._buffer):
            if user != register_user:
                try:
                    callbackhandler = self._buffer[register_user]
                    # mandatory to prevent crash about ownership
                    callbackhandler._pyroClaimOwnership() 
                    callbackhandler.recv(user, message)
                    self._log.info(f"message send to {register_user}")
                except ConnectionClosedError:
                    self._log.info(f"remove user {register_user} (disconnected)")
                    del self._buffer[register_user] 


if __name__=="__main__":
    PORT = 66666
    logging.basicConfig(level=logging.DEBUG)
    try:
        host = sys.argv[1]
    except:
        host = "127.0.0.1"

    print(f"Bind on {host}:{PORT}")   
    with Daemon(host=host, port=6666) as daemon:
        uri = daemon.register(ChatServer, "ChatServer")      
        daemon.requestLoop()
