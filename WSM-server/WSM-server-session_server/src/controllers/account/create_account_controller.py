
from src.config.wsm_logger import logger
from src.enums.types import JourneyType
from src.factories.accounts.work_time_manager_factory import WorkTimeManagerFactory
from src.models.dto.account_dto import AccountDTO
from src.utils.transform_models import account_dto_to_standard_work_hours_schema, account_dto_to_flex_time_schema
from src.services.pooling.accounts_pooling_service import AccountsPoolingService


class CreateAccountController:

    @staticmethod
    async def execute(account: AccountDTO):
        uid = account.uid

        try:
            logger.info(f"Starting process to create user {account.uid} ")
            logger.debug(f"Data received from account create endpoint {account}")

            create_account_factory = WorkTimeManagerFactory()
            create_account_service = create_account_factory.create(account)

            if account.journey != JourneyType.FLEX_TIME:
                logger.debug(f"Transforming {uid} for standard work hour default")
                standard_work_hours = account_dto_to_standard_work_hours_schema(account)
            else:
                logger.debug(f"Transforming {uid} for standard work hour flex")
                standard_work_hours = account_dto_to_flex_time_schema(account)

            uid = await create_account_service.insert(standard_work_hours)
            logger.info(f"Account {uid} added successfully to the database")
        except Exception as e:
            logger.error(f"Could not insert entry {uid} on database, reason: {e} ")
        else:
            try:
                logger.info(f"Starting process account pooling to update account {uid}")
                await AccountsPoolingService.execute(uid)
            except Exception as e:
                logger.error(f"Could not process entry {uid} on account pooling, reason: {e} ")