from src.config.wsm_logger import logger
from src.models.schema.request_models import StandardWorkHoursSchema
from src.services.account.insert_account_database_service import InsertAccountDatabaseService
from src.services.account.search_account_by_uid_service import SearchAccountByUIDService
from src.services.targets.configure_account_targets_status import ConfigureAccountTargets


class CreateAccountAndTargetsService:

    @staticmethod
    async def execute(standard_work_hours: StandardWorkHoursSchema) -> str:
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