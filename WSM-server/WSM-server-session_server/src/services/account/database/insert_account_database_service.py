import json

from src.connections.database_manager import DatabaseManager
from src.models.models import StandardWorkHours
from src.models.schema.request_models import StandardWorkHoursSchema


class InsertAccountDatabaseService:

    @staticmethod
    async def execute(standard_work_hours: StandardWorkHoursSchema):
        entry = standard_work_hours.model_dump()
        account_data = StandardWorkHours(**entry)

        database_manager = DatabaseManager()
        database_manager.add_entry(account_data)