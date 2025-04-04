from src.config.wsm_logger import logger
from src.connections.database_manager import DatabaseManager
from src.models.models import StandardWorkHours
from src.models.schema.request_models import StandardWorkHoursSchema
from src.services.account.database.insert_account_database_service import InsertAccountDatabaseService
from src.services.account.presenter.search_account_by_uid_service import SearchAccountByUIDService
from src.services.account.manager.work_time_manager import WorkTimeManager
from src.services.targets.configure_account_targets_status import ConfigureAccountTargets


class FixedWorkTimeManager(WorkTimeManager):
    async def insert(self, standard_work_hours: StandardWorkHoursSchema) -> str:
        uid = standard_work_hours.uid
        account_data = standard_work_hours.model_dump()
        await InsertAccountDatabaseService.execute(standard_work_hours)

        account = await SearchAccountByUIDService.execute(uid)

        if account:
            logger.info(f"Entry {account_data} added successfully in the database")
            await ConfigureAccountTargets.execute(account.id)
        else:
            raise Exception(f"Account \"{uid} not inserted into database.")

        return uid

    async def update(self, standard_work_hours: StandardWorkHoursSchema):
        uid = standard_work_hours.uid

        dm = DatabaseManager()
        account: StandardWorkHours | None = dm.get_by_uid(StandardWorkHours, uid)

        if account:
            entry = standard_work_hours.model_dump()
            dm.update_entry(StandardWorkHours, account.id, entry)

            return account
        else:
            raise Exception(f"Account \"{uid}\" not found in the database")

