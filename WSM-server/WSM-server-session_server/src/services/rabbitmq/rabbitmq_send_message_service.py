from src.services.MQ_Producer_service import RabbitMQProducer


class RabbitMQSendMessageService:

    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.producer = RabbitMQProducer(queue_name)

    def send(self, message: dict):
        self.producer.send_message(message)