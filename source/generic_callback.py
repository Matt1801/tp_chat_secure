import logging

from Pyro5.api import expose, callback

class GenericCallback(object):

    def __init__(self) -> None:
        self._fifo = list()
        self._log = logging.getLogger(self.__class__.__name__)

    @expose
    @callback
    def recv(self, user, message):
        self._log.debug(f"Received : {user} -> {message}")
        self._fifo.append((user, message))

    def get(self)->list:
        return self._fifo

    def clear(self)->None:
        self._fifo.clear()