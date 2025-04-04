
from src.config.wsm_logger import logger
from src.factories.accounts.create_account_and_targets_factory import CreateAccountAndTargetsFactory
from src.models.schema.request_models import StandardWorkHoursSchema
from src.services.pooling.accounts_pooling_service import AccountsPoolingService


class CreateAccountController:

    @staticmethod
    async def execute(standard_work_hours: StandardWorkHoursSchema):
        try:
            create_account_factory = CreateAccountAndTargetsFactory()
            create_account_service = create_account_factory.create(standard_work_hours)

            uid = await create_account_service.execute(standard_work_hours)
        except Exception as e:
            logger.error(f"Could not insert entry {standard_work_hours.model_dump()} on database, reason: {e} ")
        else:
            try:
                logger.info(f"Starting process account pooling to update account {uid}")
                await AccountsPoolingService.execute(uid)
            except Exception as e:
                logger.error(f"Could not process entry {standard_work_hours.model_dump()} on account pooling, reason: {e} ")