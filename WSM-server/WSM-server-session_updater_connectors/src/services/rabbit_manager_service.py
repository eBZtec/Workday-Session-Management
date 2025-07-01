import pika
import json
from src.logs.logger import logger
from src.config import config

class RabbitMQManagerService:
    def __init__(self, host):
        try:
            credentials = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PWD)
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=credentials))
            self.channel = self.connection.channel()
        except Exception as e:
            logger.error(f"Error initializing RabbitMQManager: {e}")
            raise

    def declare_queue(self, queue_name):
        """
        Declare queue into RabbitMQ.
        """
        try:
            self.channel.queue_declare(queue=queue_name, durable=True)
            logger.info(f"WSM - Session Updater Connectors - RabbitMQ Manager Service - Queue declared: {queue_name}")
        except Exception as e:
            logger.error(f"WSM - Session Updater Connectors - RabbitMQ Manager Service -Error declaring queue {queue_name}: {e}")
            raise

    def consume_messages(self, queue_name, callback):
        """
        Consume messages continuously (block mode).
        """

        try:
            self.channel.basic_consume(queue=queue_name, on_message_callback= callback, auto_ack= True)
            logger.info(f"Started consuming messages from queue: {queue_name}")
            #start block consume
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error consuming messages from queue {queue_name}: {e}")
            raise


    def send_message(self, queue_names, message):
        """
        Send messages to queue
        """
        
        #add the session agent updater queue into queues list do send message
        #all_queues = queue_names+[config.RABBITMQ_SESSION_AGENT_QUEUE_NAME]

        for queue_name in queue_names:
            try:
                self.channel.queue_declare(queue=queue_name, durable=True)
                self.channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(delivery_mode=2)  # Torna a mensagem persistente
                )
                logger.info(f"WSM - Session Updater COnnectors - RabbitMQ Manager Service - Message sent to queue {queue_name}: {message}")
            except Exception as e:
                logger.error(f"WSM - Session Updater COnnectors - RabbitMQ Manager Service - Error sending message to queue {queue_name}: {e}")
                raise


    def close(self):
        """
        Fecha a conexão com o RabbitMQ.
        """
        try:
            self.connection.close()
            logger.info("WSM - Session Updater COnnectors - RabbitMQ Manager Service - RabbitMQManager connection closed.")
        except Exception as e:
            logger.error(f"WSM - Session Updater COnnectors - RabbitMQ Manager Service - Error closing RabbitMQ connection: {e}")
            raise