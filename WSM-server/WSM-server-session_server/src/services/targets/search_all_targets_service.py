from src.connections.database_manager import DatabaseManager
from src.models.models import Target


class SearchAllTargetsService:

    @staticmethod
    async def execute() -> list[Target] | None:
        database_manager = DatabaseManager()

        return database_manager.get_all_targets()