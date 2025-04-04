
from src.config.wsm_logger import logger
from src.factories.accounts.work_time_manager_factory import WorkTimeManagerFactory
from src.models.dto.account_dto import AccountDTO
from src.utils.transform_models import account_dto_to_standard_work_hours_schema
from src.services.pooling.accounts_pooling_service import AccountsPoolingService


class CreateAccountController:

    @staticmethod
    async def execute(account: AccountDTO):
        standard_work_hours = {}

        try:
            create_account_factory = WorkTimeManagerFactory()
            create_account_service = create_account_factory.create(account)

            standard_work_hours = account_dto_to_standard_work_hours_schema(account)
            logger.debug(f"Account data to added {standard_work_hours.model_dump()} to the creation endpoint")

            uid = await create_account_service.insert(standard_work_hours)
            logger.info(f"Account {uid} added successfully to the database")
        except Exception as e:
            logger.error(f"Could not insert entry {standard_work_hours.model_dump()} on database, reason: {e} ")
        else:
            try:
                logger.info(f"Starting process account pooling to update account {uid}")
                await AccountsPoolingService.execute(uid)
            except Exception as e:
                logger.error(f"Could not process entry {uid} on account pooling, reason: {e} ")