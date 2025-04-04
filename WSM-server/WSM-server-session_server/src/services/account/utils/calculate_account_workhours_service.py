from datetime import time

from src.connections.database_manager import DatabaseManager
from src.utils.timeframes_helper import clean_work_timeframes
from src.utils.week_day_helper import update_work_week_days
from src.services.overtime.get_overtimes_by_account_uid_service import GetOvertimesByAccountUidService
from src.services.holidays.search_next_holidays_by_city_service import SearchNextHolidaysByCityService
from src.utils.work_hours_helper import generate_overtime_hours, generate_work_hours, allowed_work_days_as_json



class CalculateWorkhoursService:


    def __init__(self, uid: str, start_work_hour: time, end_work_hour: time, city: int, week_days: str, unrestricted = False, enable = True):
        self.uid = uid
        self.start_work_hour = start_work_hour
        self.end_work_hour = end_work_hour
        self.city = city
        self.week_days = week_days
        self.enable = enable

        if unrestricted:
            self.start_work_hour = time(0,0)
            self.end_work_hour = time(23,59)
            self.week_days = "1111111"

        if not enable:
            self.week_days = "1111111"
            self.start_work_hour = time(0, 0)
            self.end_work_hour = time(0, 1)

        self.database_manager = DatabaseManager()

    def calculate(self) -> str:
        active_overtimes = []
        if self.enable:
            active_overtimes = GetOvertimesByAccountUidService.execute(self.uid)

        active_holidays = SearchNextHolidaysByCityService.execute(self.city)

        updated_work_week_days = update_work_week_days(self.week_days, holidays=active_holidays)
        work_overtimes = generate_overtime_hours(active_overtimes)
        work_hours = generate_work_hours(updated_work_week_days, self.start_work_hour, self.end_work_hour)

        timeframes = work_hours + work_overtimes

        timeframes_clean = clean_work_timeframes(timeframes)
        return allowed_work_days_as_json(timeframes_clean)

