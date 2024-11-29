from src.connections.database_manager import DatabaseManager
from src.models.models import ExtendedWorkHours
from src.models.schema.request_models import ExtendedWorkHoursSchema


class UpdateOvertimeDatabaseService:

    @staticmethod
    async def execute(overtime_id: int, overtime: ExtendedWorkHoursSchema):
        database_manager = DatabaseManager()

        database_overtime = database_manager.get_by_id(ExtendedWorkHours, overtime_id)

        if database_overtime:
            entry = overtime.model_dump()
            database_manager.update_entry(ExtendedWorkHours, overtime_id, entry)
        else:
            raise Exception(f"Overtime id {overtime_id} not found on database")