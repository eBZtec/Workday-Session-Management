from src.connections.database_manager import DatabaseManager
from src.models.models import StandardWorkHours
from src.models.schema.request_models import StandardWorkHoursSchema


class UpdateAccountDatabaseService:

    @staticmethod
    async def execute(standard_work_hours: StandardWorkHoursSchema) -> StandardWorkHours:
        uid = standard_work_hours.uid

        dm = DatabaseManager()
        account: StandardWorkHours | None = dm.get_by_uid(StandardWorkHours, uid)

        if account:
            entry = standard_work_hours.model_dump()
            dm.update_entry(StandardWorkHours, account.id, entry)

            return account
        else:
            raise Exception(f"Account \"{uid}\" not found in the database")