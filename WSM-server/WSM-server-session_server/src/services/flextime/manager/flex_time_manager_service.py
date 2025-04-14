from datetime import datetime

from src.config.wsm_logger import logger
from src.connections.database_manager import DatabaseManager
from src.enums.types import WorkTimeType
from src.models.models import FlexTime
from src.services.flextime.presenter.get_last_work_time_by_user import GetLastWorkTimeByUser


class FlexTimeManagerService:

    def __init__(self):
        self.dm = DatabaseManager()

    def insert(self, uid: str, _id: int, work_time: datetime):
        last_work_time = GetLastWorkTimeByUser.get(_id)
        work_time_type = WorkTimeType.IN

        if last_work_time:
            logger.info(f"Found last work time for user {uid}")
            logger.debug(f"Last work time found {last_work_time} for user {uid}")

            if last_work_time.work_time_type == WorkTimeType.IN:
                logger.debug(f"Work time {last_work_time} is defined as IN. New work time is defined as OUT.")
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