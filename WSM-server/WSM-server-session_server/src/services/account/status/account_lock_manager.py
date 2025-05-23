from src.config import config
from src.config.wsm_logger import logger
from src.services.rabbitmq.rabbitmq_send_message_service import RabbitMQSendMessageService


class AccountLockManager:

    @staticmethod
    async def lock(uid: str):
        logger.info(f"Starting process to lock account {uid}")
        rabbitmq_send_message = RabbitMQSendMessageService(queue_name=config.WSM_CONNECTOR_AD_QUEUE_NAME)

        message = {
            "uid": uid,
            "status": "success",
            "message": "",
            "account_unlock": True
        }
        rabbitmq_send_message.send(message)
        logger.info(f"Finishing process to lock account {uid}")

    @staticmethod
    async def unlock(uid: str):
        logger.info(f"Starting process to unlock account {uid}")
        rabbitmq_send_message = RabbitMQSendMessageService(queue_name=config.WSM_CONNECTOR_AD_QUEUE_NAME)

        message = {
            "uid": uid,
            "status": "success",
            "message": "",
            "account_unlock": False
        }
        rabbitmq_send_message.send(message)
        logger.info(f"Finishing process to unlock account {uid}")