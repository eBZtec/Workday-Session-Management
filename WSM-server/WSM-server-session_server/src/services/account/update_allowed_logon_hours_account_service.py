from src.config.wsm_logger import logger
from src.services.account.calculate_account_workhours_service import CalculateWorkhoursService
from src.services.account.search_account_by_uid_service import SearchAccountByUIDService
from src.services.account.update_account_attribute_service import UpdateAccountAttributeService
from src.utils.work_hours_helper import string_to_time


class UpdateAllowedLogonHoursAccountService:

    @staticmethod
    async def execute(uid: str):
        account = await SearchAccountByUIDService.execute(uid)

        if account:
            logger.info(f"Found account {account.__dict__} for uid \"{account.uid}\"")
            uid = account.uid
            start_work_hour = string_to_time(account.start_time)
            end_work_hour = string_to_time(account.end_time)
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
            await UpdateAccountAttributeService.execute(account.id, "allowed_work_hours", allowed_work_hours)
        else:
            raise Exception(f"Account {uid} not found.")