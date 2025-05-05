import json
from datetime import datetime, timedelta

from src.config.wsm_logger import logger


class FormatWorkHoursService:
    @staticmethod
    async def format(work_hours: str) -> str | None:
        try:
            work_hours: dict = json.loads(work_hours)
            logger.debug(f"Work hours defined as {work_hours}")
            today = datetime.today()
            today_week_day = today.weekday()

            week_map = {
                0: "MONDAY",
                1: "TUESDAY",
                2: "WEDNESDAY",
                3: "THURSDAY",
                4: "FRIDAY",
                5: "SATURDAY",
                6: "SUNDAY"
            }

            week_day = week_map.get(today_week_day)

            if week_day in work_hours:
                today_work_hours: list = work_hours.get(week_day)

                if len(today_work_hours) == 1:
                    first_today_work_hour = today_work_hours[0]
                    start_time = first_today_work_hour.get("start")
                    end_time = first_today_work_hour.get("end")

                    result = {
                        "start": str(timedelta(minutes=start_time)),
                        "end": str(timedelta(minutes=end_time)),
                    }
                    return str(result)
                elif len(today_work_hours) > 0:
                    first_today_work_hour = today_work_hours[0]
                    last_today_work_hour = today_work_hours[-1]

                    start_time = first_today_work_hour.get("start")
                    end_time = last_today_work_hour.get("end")

                    result = {
                        "start": str(timedelta(minutes=start_time)),
                        "end": str(timedelta(minutes=end_time)),
                    }

                    return str(result)
        except Exception as e:
            logger.warn(f"Could not format work hours, reason: {e}")
        return None