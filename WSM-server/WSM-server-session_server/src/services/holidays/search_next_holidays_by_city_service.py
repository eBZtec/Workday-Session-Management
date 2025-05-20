from datetime import date

from src.connections.database_manager import DatabaseManager


class SearchNextHolidaysByCityService:

    @staticmethod
    def execute(city: str):
        database_manager = DatabaseManager()

        start_date = date.today()
        end_date = date.fromordinal(start_date.toordinal() + 6)

        holidays_found = database_manager.get_holidays(city)
        holidays_active: list[date] = []

        for holiday in holidays_found:
            holiday_date = date(start_date.year, holiday.month, holiday.day)

            if start_date <= holiday_date <= end_date:
                holidays_active.append(holiday_date)

        return holidays_active