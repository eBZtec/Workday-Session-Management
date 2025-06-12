import json
from datetime import datetime, date

from src.config.wsm_logger import logger


class FormatWorkHoursService:
    @staticmethod
    async def format(work_hours: str) -> str | None:
        try:
            work_hours: dict = json.loads(work_hours)
            logger.debug(f"Work hours defined as {work_hours}")
            result = None

            if "start" in work_hours:
                start_time = datetime.fromisoformat(work_hours["start"])

                logger.debug(f"Today is {date.today()}")

                if start_time.date() == date.today():
                    logger.debug(f"Start time {start_time} is today {date.today()}")
                    result = work_hours

            return str(result)
        except Exception as e:
            logger.warning(f"Could not format work hours, reason: {e}")
        return None