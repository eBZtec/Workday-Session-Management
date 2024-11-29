from src.connections.database_manager import DatabaseManager
from src.models.models import StandardWorkHours


class SearchAccountByUIDService:

    @staticmethod
    async def execute(uid: str) -> StandardWorkHours:
        database_manager = DatabaseManager()

        return database_manager.get_by_uid(StandardWorkHours, uid)