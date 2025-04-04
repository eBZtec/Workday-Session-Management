from src.config import config
from src.config.wsm_logger import logger
from src.models.models import StandardWorkHours
from src.services.account.presenter.search_account_by_uid_service import SearchAccountByUIDService
from src.services.account.database.update_allowed_logon_hours_account_service import UpdateAllowedLogonHoursAccountService
from src.services.rabbitmq.rabbitmq_send_message_service import RabbitMQSendMessageService


class AccountsPoolingService:

    @staticmethod
    async def execute(uid: str):
        await UpdateAllowedLogonHoursAccountService.execute(uid)
        account = await SearchAccountByUIDService.execute(uid)

        if account:
            logger.info(f"Found account {account.__dict__} for uid \"{account.uid}\"")
            rabbitmq_send_message = RabbitMQSendMessageService(queue_name=config.WORK_HOURS_QUEUE)

            message = account.__dict__
            rabbitmq_send_message.send(message)

            logger.info(f"Message {message} successfully sent to queue \"{config.WORK_HOURS_QUEUE}\"")

    @staticmethod
    async def execute_with_account(account: StandardWorkHours):

        rabbitmq_send_message = RabbitMQSendMessageService(queue_name=config.WORK_HOURS_QUEUE)

        message = account.__dict__
        rabbitmq_send_message.send(message)

        logger.info(f"Message {message} successfully sent to queue \"{config.WORK_HOURS_QUEUE}\"")