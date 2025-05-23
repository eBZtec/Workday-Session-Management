from src.config import config
from src.config.wsm_logger import logger
from src.services.rabbitmq.rabbitmq_send_message_service import RabbitMQSendMessageService


class ActiveDirectoryAccountStatusManager:

    @staticmethod
    async def enable(uid: str):
        logger.info(f"Starting process to enable Active Directory account {uid}")
        rabbitmq_send_message = RabbitMQSendMessageService(queue_name=config.WSM_AGENT_NOTIFICATION_QUEUE)

        message = {
            "uid": uid,
            "status": "success",
            "message": "",
            "account_status": True
        }
        rabbitmq_send_message.send(message)

        logger.info(f"Finishing process to enable Active Directory account {uid}")

    @staticmethod
    async def disable(uid: str):
        logger.info(f"Starting process to disable Active Directory account {uid}")
        rabbitmq_send_message = RabbitMQSendMessageService(queue_name=config.WSM_AGENT_NOTIFICATION_QUEUE)

        message = {
            "uid": uid,
            "status": "success",
            "message": "",
            "account_status": False
        }
        rabbitmq_send_message.send(message)
        logger.info(f"Finishing process to disable Active Directory account {uid}")