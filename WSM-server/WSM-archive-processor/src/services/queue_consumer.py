import pika
from src.config import config

class QueueConsumer:
    def __init__(self, queue_name, host=config.QUEUE_HOST):
        self.queue_name = queue_name
        self.connection_params = pika.ConnectionParameters(host)
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def start_consuming(self, callback):
        print(f"[*] Waiting for messages into queue: '{self.queue_name}'. Push CTRL+C to exit.")
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=False)
        self.channel.start_consuming()

    def acknowledge_message(self, delivery_tag):
        self.channel.basic_ack(delivery_tag=delivery_tag)
