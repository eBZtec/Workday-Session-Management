import pika
from src.logs.logger import Logger


class RabbitMQConsumer:
    """
    Classe responsável por consumir mensagens da fila RabbitMQ.
    """

    def __init__(self, host, queue, callback):
        self.logger = Logger(log_name=self.__class__.__name__).get_logger()
        self.host = host
        self.queue = queue
        self.callback = callback

    def start(self):
        """
        Inicia o consumidor RabbitMQ.
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
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