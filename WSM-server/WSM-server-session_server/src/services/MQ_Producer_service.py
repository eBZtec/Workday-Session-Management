import json

import pika
from dotenv import load_dotenv

from src.config import config
from src.config.wsm_logger import logger

load_dotenv()

class RabbitMQProducer:
    def __init__(self, queue_name: str, ):
        self.queue_name = queue_name
        self.host = config.MQ_ADDRESS_HOST
        self.port = config.MQ_HOST_PORT
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        params = pika.ConnectionParameters(host=self.host, port=self.port)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        # Declare queue
        self.channel.queue_declare(queue=self.queue_name, durable=True)
    
    def send_message(self, message: dict):
        if self.channel is None:
            logger.error("Could not establish RabbitMQ connection")
            raise ConnectionError("Could not establish RabbitMQ connection")

        message_body = json.dumps(message, default=str)
        
        # Publish in the queue
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )

    def close_connection(self):
        if self.connection:
            self.connection.close()
