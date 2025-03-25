
from src.config.wsm_logger import logger
from src.models.schema.request_models import StandardWorkHoursSchema
from src.services.account.calculate_account_workhours_service import CalculateWorkhoursService
from src.services.account.create_account_and_targets_service import CreateAccountAndTargetsService
from src.services.account.insert_account_database_service import InsertAccountDatabaseService
from src.services.account.search_account_by_uid_service import SearchAccountByUIDService
from src.services.pooling.accounts_pooling_service import AccountsPoolingService
from src.services.targets.configure_account_targets_status import ConfigureAccountTargets
from src.utils.work_hours_helper import string_to_time


class CreateAccountController:

    @staticmethod
    async def execute(standard_work_hours: StandardWorkHoursSchema):
        try:
            uid = await CreateAccountAndTargetsService.execute(standard_work_hours)
        except Exception as e:
            logger.error(f"Could not insert entry {standard_work_hours.model_dump()} on database, reason: {e} ")
        else:
            try:
                logger.info(f"Starting process account pooling to update account {uid}")
                await AccountsPoolingService.execute(uid)
            except Exception as e:
                logger.error(f"Could not process entry {standard_work_hours.model_dump()} on account pooling, reason: {e} ")