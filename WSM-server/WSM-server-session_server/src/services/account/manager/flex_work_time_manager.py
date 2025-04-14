from src.config.wsm_logger import logger
from src.connections.database_manager import DatabaseManager
from src.models.models import StandardWorkHours
from src.models.schema.request_models import FlexTimeSchema
from src.services.account.database.insert_account_database_service import InsertAccountDatabaseService
from src.services.account.manager.work_time_manager import WorkTimeManager
from src.services.account.presenter.search_account_by_uid_service import SearchAccountByUIDService
from src.services.flextime.manager.flex_time_manager_service import FlexTimeManagerService
from src.services.targets.configure_account_targets_status import ConfigureAccountTargets
from src.utils.transform_models import flex_time_schema_standard_work_hours


class FlexWorkTimeManager(WorkTimeManager):
    async def insert(self, standard_work_hours: FlexTimeSchema) -> str:
        uid = standard_work_hours.uid
        logger.info(f"Starting process to insert new flex time hours for user {uid}")
        work_hours = flex_time_schema_standard_work_hours(standard_work_hours)
        work_time = standard_work_hours.work_time

        await InsertAccountDatabaseService.execute(work_hours)

        account = await SearchAccountByUIDService.execute(uid)

        if account:
            logger.info(f"Entry {uid} added successfully in the database")
            FlexTimeManagerService().insert(uid, account.id, work_time)
            await ConfigureAccountTargets.execute(account.id)
        else:
            raise Exception(f"Account \"{uid} not inserted into database.")

        return uid

    async def update(self, standard_work_hours: FlexTimeSchema):
        uid = standard_work_hours.uid
        logger.info(f"Starting process to insert new flex time hours for user {uid}")
        work_hours = flex_time_schema_standard_work_hours(standard_work_hours)
        work_time = standard_work_hours.work_time

        dm = DatabaseManager()
        account: StandardWorkHours | None = dm.get_by_uid(StandardWorkHours, uid)

        if account:
            entry = work_hours.model_dump()
            dm.update_entry(StandardWorkHours, account.id, entry)

            FlexTimeManagerService().insert(uid, account.id, work_time)

            return account
        else:
            raise Exception(f"Account \"{uid}\" not found in the database")