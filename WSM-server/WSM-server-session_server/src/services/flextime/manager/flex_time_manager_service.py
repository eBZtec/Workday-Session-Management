from datetime import datetime, timedelta, timezone

from src.config.wsm_logger import logger
from src.connections.database_manager import DatabaseManager
from src.enums.types import WorkTimeType
from src.models.models import FlexTime, StandardWorkHours
from src.services.flextime.presenter.get_last_work_time_by_user import GetLastWorkTimeByUser


FORMATO = "%H:%M"


class FlexTimeManagerService:

    def __init__(self):
        self.dm = DatabaseManager()

    def insert(self, account: StandardWorkHours, work_time: datetime):
        uid = account.uid
        _id = account.id

        last_work_time = GetLastWorkTimeByUser.get(_id)
        work_time_type = WorkTimeType.IN

        if last_work_time:
            logger.info(f"Found last work time for user {uid}")
            logger.debug(f"Last work time found \"{last_work_time.work_time}\" type \"{last_work_time.work_time_type}\" for user {uid}")

            if last_work_time.work_time_type == WorkTimeType.IN:
                user_work_hour = FlexTimeManagerService.calculate_work_hours_quantity(account.start_time, account.end_time)
                logger.info(f"Account {uid} work hours quantity is: {user_work_hour / 3600} hours")

                work_time_quantity = FlexTimeManagerService.get_difference_in_hours_between_work_times(last_work_time.work_time, work_time)
                logger.info(f"Difference between the last work time for the current work time is: {work_time_quantity / 3600} hours for account {account.uid}")

                if work_time_quantity > user_work_hour:
                    logger.info(f"Current work will be defined as IN. Difference between the last work time is more than account {account.uid} journey")
                    work_time_type = WorkTimeType.IN
                else:
                    logger.info(f"Work time {last_work_time} is defined as IN. New work time is defined as OUT.")
                    work_time_type = WorkTimeType.OUT
        else:
            logger.debug(f"No work time found for user {uid}, work time {work_time} will be considered as IN.")

        new_flex_time = FlexTime()
        new_flex_time.std_wrk_id = _id
        new_flex_time.work_time = work_time
        new_flex_time.work_time_type = work_time_type

        logger.debug(f"New work time defined as {new_flex_time}")

        self.dm.add_entry(new_flex_time)

        logger.info(f"Work time added successfully for user {uid}")

    @staticmethod
    def get_difference_in_hours_between_work_times(last_work_time: datetime, work_time: datetime, tz = timezone.utc):

        def _to_utc(dt: datetime) -> datetime:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz)
            return dt.astimezone(timezone.utc)

        delta: timedelta = _to_utc(work_time) - _to_utc(last_work_time)

        return abs(delta.total_seconds())

    @staticmethod
    def calculate_work_hours_quantity(start_hour: str, end_hour: str) -> int:
        t_in = datetime.strptime(start_hour, FORMATO)
        t_out = datetime.strptime(end_hour, FORMATO)

        if t_out <= t_in:
            t_out += timedelta(days=1)

        duration = t_out - t_in

        return int(duration.total_seconds())