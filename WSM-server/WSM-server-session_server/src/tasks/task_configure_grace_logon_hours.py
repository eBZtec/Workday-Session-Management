from datetime import datetime, date, timedelta

from src.config import config
from src.config.wsm_logger import logger
from src.connections.database_manager import DatabaseManager
from src.enums.types import WorkTimeType
from src.models.models import StandardWorkHours
from src.services.account.database.update_account_attribute_service import UpdateAccountAttributeService
from src.services.account.utils.calculate_account_workhours_service import CalculateWorkhoursService
from src.services.flextime.presenter.get_last_work_time_by_user import GetLastWorkTimeByUser
from src.services.rabbitmq.rabbitmq_send_message_service import RabbitMQSendMessageService
from src.utils.work_hours_helper import string_to_time


async def execute():
    logger.info("Starting task to update AD logon hours got Flex Time accounts")
    database_manager = DatabaseManager()

    flex_time_accounts = database_manager.get_users_by_journey_type()

    for account in flex_time_accounts:
        try:
            logger.info(f"Grace logon task - Processing user {account.uid}")
            _id = account.id
            uid = account.uid

            last_work_time = GetLastWorkTimeByUser.get(_id)

            if last_work_time is not None:
                current_work_time: datetime = last_work_time.work_time

                if last_work_time.work_time_type == WorkTimeType.IN and is_today(current_work_time):
                    logger.info(f"Grace logon task - Ignoring account {uid}, current work time is today, Account is working...")
                    return

            start_work_hour = string_to_time(subtract_hours_hhmm_dt(account.start_time))
            end_work_hour = string_to_time(add_hours_hhmm_dt(account.start_time))
            city = account.c
            week_work_days = account.weekdays
            unrestricted = account.unrestricted
            enable = account.enable

            calculate_work_hours_service = CalculateWorkhoursService(
                uid,
                start_work_hour,
                end_work_hour,
                city,
                week_work_days,
                unrestricted,
                enable
            )
            allowed_work_hours = calculate_work_hours_service.calculate()
            logger.info(f"Grace logon task - Allowed logon hours defined as {allowed_work_hours} for account {uid}")

            await UpdateAccountAttributeService.execute(account.id, "logon_hours", allowed_work_hours)
            send_message(database_manager, _id)
            logger.info(f"Grace logon task - Pooling account update sent for account {uid}")
        except Exception as e:
            logger.error(f"Grace logon task - Could not process account {account.uid}, reason: {e}")


def subtract_hours_hhmm_dt(hora: str, horas_sub: int = 3) -> str:
    base = datetime.strptime(hora, "%H:%M")
    result = base - timedelta(hours=horas_sub)

    return result.strftime("%H:%M")

def add_hours_hhmm_dt(hora: str, horas_add: int = 3) -> str:
    base = datetime.strptime(hora, "%H:%M")
    result = base + timedelta(hours=horas_add)

    return result.strftime("%H:%M")


def is_today(dt: datetime):
    if dt.date() == date.today():
        return True
    return False


def send_message(dm: DatabaseManager, _id: int):
    account = dm.get_by_id(StandardWorkHours, _id)

    if account:
        logger.info(f"Sending connector update for account {account.__dict__} for uid \"{account.uid}\"")

        rabbitmq_send_message = RabbitMQSendMessageService(queue_name=config.WORK_HOURS_QUEUE)

        message = account.__dict__
        rabbitmq_send_message.send(message)

        logger.info(f"Message {message} successfully sent to queue \"{config.WORK_HOURS_QUEUE}\"")
    else:
        logger.warning(f"Account id {_id} not found")
