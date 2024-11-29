from src.connections.database_manager import DatabaseManager
from src.models.models import ExtendedWorkHours
from src.models.schema.request_models import ExtendedWorkHoursSchema


class InsertOvertimeDatabaseService:

    @staticmethod
    async def execute(overtime_data: ExtendedWorkHoursSchema, account_id: int):
        entry = overtime_data.model_dump()
        overtime = ExtendedWorkHours(**entry)

        overtime.std_wrk_id = account_id

        database_manager = DatabaseManager()
        database_manager.add_entry(overtime)