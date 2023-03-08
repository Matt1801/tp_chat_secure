import threading
import time
import sys
import logging

from Pyro5.api import Daemon, Proxy
from Pyro5.errors import ConnectionClosedError,CommunicationError

from generic_callback import GenericCallback

# https://github.com/irmen/Pyro5/blob/master/examples/callback/client2.py

class ChatClient:
    def __init__(self, host:str, port:int) -> None:
        self._uri = f"PYRO:ChatServer@{host}:{port}"
        self._daemon = None
        self._running = False
        self._callback = None
        self._name = ""
        self._log = logging.getLogger(self.__class__.__name__)

    def start(self, callback:object)->None:
        self._daemon = Daemon()
        self._callback = callback
        self._daemon.register(self._callback)
        self._running = True
        thread = threading.Thread(target=self._daemon.requestLoop,kwargs={"loopCondition":self._loop_condition}, daemon=True)
        thread.start()

    def _loop_condition(self)->bool:
        if self._running == False:
            self._daemon = None
            self._callback = None
            self._name = ""
        return self._running

    def stop(self)->None:
        self._running = False

    def register(self, name:str)->None:
        self._name = name
        with Proxy(self._uri) as server:
            server.register(self._name, self._callback)

    def send_message(self, message:str)->None:
        with Proxy(self._uri) as server:    
            server.send_message(self._name, message)

if __name__=="__main__":
    # example main function
    # command : python3 chat_client.py 127.0.0.1 foo
    # send every second a message; by running two instances (with another name, like bar), you
    # will see a discussion :)
    PORT = 6666
    host = sys.argv[1]
    name = sys.argv[2]
    logging.basicConfig(level=logging.DEBUG)

    fifo = GenericCallback()

    client = ChatClient(host, PORT)
    client.start(fifo)
    client.register(name)

    while True:
        try:
            client.send_message(f"hello at {int(time.time())}")
        except ConnectionClosedError:
            print("server closed, bye")
            break
        except CommunicationError:
            print("server shutdown, bye")
            break

        print(fifo.get())
        fifo.clear()

        time.sleep(1)