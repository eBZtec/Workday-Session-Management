import pika

from src.config.wsm_config import wsm_config
from src.shared.generic.singleton import Singleton


class SingletonQueueManager(type):
    _instances = {}

    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls._instances[cls] = super().__call__()
        print(cls._instances)

    def __call__(cls, *args, **kwargs):
        return cls._instances[cls]


class WSMQueueManager(metaclass=Singleton):
    def __init__(self):

        self.connection = None
        self.channel = None

        self._init_connection()

    def _init_connection(self):
        host = wsm_config.wsm_queue_host
        port = wsm_config.wsm_queue_port

        user = wsm_config.wsm_queue_user
        password = wsm_config.wsm_queue_user_password
        queue_name = wsm_config.wsm_queue_updater

        credentials = pika.PlainCredentials(user, password)
        params = pika.ConnectionParameters(host=host, port=port, credentials=credentials)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=queue_name, durable=True)


wsm_queue_manager = WSMQueueManager()