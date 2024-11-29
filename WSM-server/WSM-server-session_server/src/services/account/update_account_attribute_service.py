from typing_extensions import Any

from src.connections.database_manager import DatabaseManager
from src.models.models import StandardWorkHours


class UpdateAccountAttributeService:

    @staticmethod
    async def execute(uid: int, attribute: str, value: Any):
        database_manager = DatabaseManager()

        entry = {attribute: value}
        database_manager.update_entry(StandardWorkHours, uid, entry)