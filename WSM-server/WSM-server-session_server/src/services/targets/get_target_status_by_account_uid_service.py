from src.connections.database_manager import DatabaseManager
from src.models.models import TargetStatus


class GetTargetStatusByAccountUidService:

    @staticmethod
    async def execute(account_id: int):
        database_manager = DatabaseManager()

        return database_manager.get_target_status_by_account_id(account_id)