
from src.services.message_processor import MessageProcessor
from src.services.rabbitMQ_consumer import RabbitMQConsumer
from src.services.zeroMQ_sender import ZeroMQSender
from src.config import config
from src.logs.logger import Logger

logger = Logger(log_name='WSM Server Agent Updater').get_logger()

def main():
    """
    Função principal que conecta as classes e inicia os serviços.
    """
    zmq_sender = ZeroMQSender(config.ZEROMQ_URL)
    processor = MessageProcessor(zmq_sender)

    def rabbitmq_callback(ch, method, properties, body):
        logger.info(f"Mensagem recebida do RabbitMQ: {body.decode()}")
        processor.process_message(body.decode())

    rabbitmq_consumer = RabbitMQConsumer(config.MQ_ADDRESS_HOST, config.MQ_AGENT_UPDATER_QUEUE, rabbitmq_callback)
    try:
        rabbitmq_consumer.start()
    finally:
        zmq_sender.close()


if __name__ == "__main__":
    main()