
import datetime

from src.config import config
from src.services.rabbitmq.rabbitmq_send_message_service import RabbitMQSendMessageService


class LogoffAccountZeroMQService:

    @staticmethod
    def logoff(uid: str, host: str):
        logoff_data = {
            "DisconnectionRequest":{
                "hostname": host,
                "user": uid,
                "dc_datetime": datetime.datetime.now(datetime.UTC)
            }
        }

        mq_message_service = RabbitMQSendMessageService(config.LOGOFF_QUEUE)
        mq_message_service.send(logoff_data)
