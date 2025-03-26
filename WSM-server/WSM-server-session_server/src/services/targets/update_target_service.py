from src.connections.database_manager import DatabaseManager
from src.models.models import Target
from src.models.schema.request_models import TargetSchema


class UpdateTargetService:
    @staticmethod
    async def execute(target_id: int, target: TargetSchema):
        database_manager = DatabaseManager()
        entry = target.model_dump()

        database_manager.update_entry(Target, target_id, entry)