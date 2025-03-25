from src.config.wsm_logger import logger
from src.models.schema.request_models import StandardWorkHoursSchema
from src.services.account.create_account_and_targets_service import CreateAccountAndTargetsService
from src.services.account.search_account_by_uid_service import SearchAccountByUIDService
from src.services.account.update_account_database_service import UpdateAccountDatabaseService
from src.services.pooling.accounts_pooling_service import AccountsPoolingService


class UpdateAccountController:

    @staticmethod
    async def execute(standard_work_hours: StandardWorkHoursSchema):
        try:
            uid = standard_work_hours.uid
            account = await SearchAccountByUIDService.execute(uid)

            if account:
                logger.info(f"Entry {account.uid} found. Entry must be updated")
                await UpdateAccountDatabaseService.execute(standard_work_hours)
            else:
                logger.info(f"Account \"{uid} not found. Entry will be created.")
                await CreateAccountAndTargetsService.execute(standard_work_hours)

            logger.info(f"Entry {standard_work_hours.model_dump()} updated successfully in the database")
        except Exception as e:
            logger.error(f"Could not update entry {standard_work_hours.model_dump()}, reason: {e}")
        else:
            try:
                logger.info(f"Starting process account pooling to update account {standard_work_hours.uid}")
                await AccountsPoolingService.execute(uid)
            except Exception as e:
                logger.error(
                    f"Could not process entry {standard_work_hours.model_dump()} on account pooling, reason: {e} ")