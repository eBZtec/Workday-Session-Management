import pika
import json
from src.logs.logger import Logger
from src.config import config

logger = Logger(log_name='WSM-Server-Agent-Updater').get_logger()
class RabbitMQManagerService:
    def __init__(self, host):
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
            self.channel = self.connection.channel()
        except Exception as e:
            logger.error(f"Error initializing RabbitMQManager: {e}")
            raise

    def declare_queue(self, queue_name):
        """
        Declara uma fila no RabbitMQ.
        """
        try:
            self.channel.queue_declare(queue=queue_name, durable=True)
            logger.info(f"WSM - Session Updater COnnectors - RabbitMQ Manager Service - Queue declared: {queue_name}")
        except Exception as e:
            logger.error(f"WSM - Session Updater COnnectors - RabbitMQ Manager Service -Error declaring queue {queue_name}: {e}")
            raise

    def consume_message(self, queue_name):
        """
        Consome uma única mensagem da fila.
        """
        try:
            method_frame, header_frame, body = self.channel.basic_get(queue=queue_name, auto_ack=True)
            if body:
                logger.info(f"Message consumed from queue {queue_name}: {body}")
                return body
        except Exception as e:
            logger.error(f"WSM - Session Updater COnnectors - RabbitMQ Manager Service - Error consuming message from queue {queue_name}: {e}")
            raise


    def send_message(self, queue_names, message):
        """
        Envia uma mensagem para a fila especificada.
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