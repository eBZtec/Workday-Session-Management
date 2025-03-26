from src.connections.database_manager import DatabaseManager
from src.models.models import Target
from src.models.schema.request_models import TargetSchema


class CreateTargetService:
    @staticmethod
    async def execute(target: TargetSchema):
        database_manager = DatabaseManager()

        entry = target.model_dump()
        entry_data = Target(**entry)

        database_manager.add_entry(entry_data)