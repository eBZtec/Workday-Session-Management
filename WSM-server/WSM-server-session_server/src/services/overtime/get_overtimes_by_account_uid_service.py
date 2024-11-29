import datetime

from src.connections.database_manager import DatabaseManager


class GetOvertimesByAccountUidService:

    @staticmethod
    def execute(uid: str):
        database_manager = DatabaseManager()

        start_date = datetime.datetime.now(datetime.UTC)
        end_date = datetime.date.fromordinal(start_date.toordinal() + 6)
        end_date = datetime.datetime(
            end_date.year,
            end_date.month,
            end_date.day,
            23,
            59,
            0,
            tzinfo=datetime.UTC
        )

        return database_manager.get_active_extensions(uid, start_date, end_date)