from src.connections.database_manager import DatabaseManager
from src.models.models import StandardWorkHours
from src.models.schema.request_models import DeactivationSchema


class DeactivateAccountDatabaseService:

    @staticmethod
    def execute(deactivate_data: DeactivationSchema) -> StandardWorkHours:
        dm = DatabaseManager()
        account: StandardWorkHours | None = dm.get_by_uid(StandardWorkHours, deactivate_data.uid)

        if account:
            payload = {'deactivation_date': deactivate_data.deactivation_time}
            dm.update_entry(StandardWorkHours, account.id, payload)

            return account
        else:
            raise Exception(f"Account \"{deactivate_data.uid}\" not found")