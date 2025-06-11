import pika
from src.logs.logger import logger
from src.config import config


class RabbitMQConsumer:
    """
    Classe responsável por consumir mensagens da fila RabbitMQ.
    """

    def __init__(self, host, queue, callback):
        self.logger = logger
        self.host = host
        self.queue = queue
        self.callback = callback

    def start(self):
        """
        Inicia o consumidor RabbitMQ.
        """
        credentials = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PWD)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=self.queue,durable=True)

        channel.basic_consume(queue=self.queue, on_message_callback=self.callback, auto_ack=True)
        self.logger.info(f"Aguardando mensagens na fila '{self.queue}'...")

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            self.logger.info("Encerrando o consumidor RabbitMQ...")
        finally:
            channel.close()
            connection.close()