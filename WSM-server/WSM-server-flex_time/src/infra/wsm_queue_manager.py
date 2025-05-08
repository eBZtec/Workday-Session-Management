import pika

from src.config.wsm_config import wsm_config
from src.config.wsm_logger import wsm_logger
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
        self.queue_name = wsm_config.wsm_queue_updater

        credentials = pika.PlainCredentials(user, password)
        params = pika.ConnectionParameters(host=host, port=port, credentials=credentials)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def start_mq(self, callback):
        self._init_connection()
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
        wsm_logger.info(f"Waiting messages on queue \"{self.queue_name}\"...")

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            wsm_logger.info("Exiting RabbitMQ consumer...")
        finally:
            self.channel.close()
            self.connection.close()

    def send_message(self, message: str, queue: str):
        if self.channel is None:
            wsm_logger.error("Could not establish RabbitMQ connection")
            raise ConnectionError("Could not establish RabbitMQ connection")

        # Publish in the queue
        self.channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )


wsm_queue_manager = WSMQueueManager()