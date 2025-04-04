from src.config.wsm_logger import logger
from src.enums.types import JourneyType
from src.factories.accounts.work_time_manager_factory import WorkTimeManagerFactory
from src.models.dto.account_dto import AccountDTO
from src.services.account.presenter.search_account_by_uid_service import SearchAccountByUIDService
from src.services.pooling.accounts_pooling_service import AccountsPoolingService
from src.utils.transform_models import account_dto_to_standard_work_hours_schema, account_dto_to_flex_time_schema


class UpdateAccountController:

    @staticmethod
    async def execute(account: AccountDTO):
        uid = account.uid

        try:
            logger.info(f"Starting process to update user {account.uid} ")
            logger.debug(f"Data received from account update endpoint {account}")

            account_manager_factory = WorkTimeManagerFactory()
            account_manager_factory = account_manager_factory.create(account)

            if account.journey != JourneyType.FLEX_TIME:
                logger.info(f"Transforming {account} for standard work hour default")
                standard_work_hours = account_dto_to_standard_work_hours_schema(account)
            else:
                logger.info(f"Transforming {account} for standard work hour flex")
                standard_work_hours = account_dto_to_flex_time_schema(account)

            account_found = await SearchAccountByUIDService.execute(uid)

            if account_found:
                logger.info(f"Entry {uid} found")
                logger.info(f"Updating user {uid} into the database")
                await account_manager_factory.update(standard_work_hours)
                logger.debug(f"Entry {standard_work_hours} updated successfully in the database")
            else:
                logger.warning(f"Account \"{uid} not found.")
                logger.info(f"Inserting user {uid} into the database")
                await account_manager_factory.insert(standard_work_hours)
                logger.info(f"User {uid} added to the database")

        except Exception as e:
            logger.error(f"Could not update entry {uid}, reason: {e}")
        else:
            try:
                logger.info(f"Starting process account pooling to update account {uid}")
                await AccountsPoolingService.execute(uid)
            except Exception as e:
                logger.error(
                    f"Could not process user {uid} on account pooling, reason: {e} ")