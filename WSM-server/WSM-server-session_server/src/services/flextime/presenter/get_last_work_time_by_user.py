from src.connections.database_manager import DatabaseManager


class GetLastWorkTimeByUser:
    @staticmethod
    def get(user_id: int):
        dm = DatabaseManager()
        return dm.get_last_flex_time_by_user_id(user_id)