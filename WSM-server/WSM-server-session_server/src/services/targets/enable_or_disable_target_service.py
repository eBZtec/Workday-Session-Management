from src.connections.database_manager import DatabaseManager
from src.models.models import Target


class EnableOrDisableTargetService:
    @staticmethod
    async def execute(target_id: int, status: int):
        database_manager = DatabaseManager()
        target: Target | None = database_manager.get_by_id(Target, target_id)

        if target:
            entry = {"enabled": status}
            database_manager.update_entry(Target, target_id, entry)
        else:
            raise Exception(f"Account not find or uid \"{target_id}\"")