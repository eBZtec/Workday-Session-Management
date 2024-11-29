from src.config.wsm_logger import logger
from src.models.schema.request_models import ExtendedWorkHoursSchema
from src.services.account.search_account_by_uid_service import SearchAccountByUIDService
from src.services.overtime.update_overtime_database_service import UpdateOvertimeDatabaseService
from src.services.pooling.accounts_pooling_service import AccountsPoolingService


class UpdateOvertimeController:

    @staticmethod
    async def execute(overtime_id: int, overtime: ExtendedWorkHoursSchema):
        try:
            account = await SearchAccountByUIDService.execute(overtime.uid)
            if account:
                await UpdateOvertimeDatabaseService.execute(overtime_id, overtime)
            else:
                raise Exception(f"Account \"{overtime.uid}\" not found. Overtime could not be updated")
        except Exception as e:
            logger.error(f"Could not insert overtime {overtime.model_dump()}, reason: {e}")
        else:
            logger.info(f"Overtime {overtime.model_dump()} inserted successfully into the database")
            try:
                logger.info(f"Starting process account pooling to update account {overtime.uid}")
                await AccountsPoolingService.execute(account.uid)
            except Exception as e:
                logger.error(f"Could not send message for data {overtime.model_dump()}, reason: {e}")