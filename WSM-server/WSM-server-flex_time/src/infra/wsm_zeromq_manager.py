import zmq

from src.config.wsm_config import wsm_config
from src.shared.generic.singleton import Singleton


class WSMZeroMQManager(metaclass=Singleton):
    def __init__(self):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind(wsm_config.wsm_zeromq_url)

    def get_socket(self):
        return self._socket


wsm_zeromq_manager = WSMZeroMQManager()