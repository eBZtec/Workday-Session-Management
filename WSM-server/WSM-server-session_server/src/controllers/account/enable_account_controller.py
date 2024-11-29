from src.config.wsm_logger import logger
from src.services.account.enable_or_disable_account_by_uid_service import EnableOrDisableAccountByUidService
from src.services.pooling.accounts_pooling_service import AccountsPoolingService


class EnableAccountController:

    @staticmethod
    async def execute(uid: str):
        try:
            await EnableOrDisableAccountByUidService.execute(uid, True)
            logger.info(f"Account \"{uid}\" enabled successfully")
        except Exception as e:
            logger.error(f"Failed to enable account \"{uid}\", reason: {e}")
        else:
            try:
                logger.info(f"Starting process account pooling to update account {uid}")
                await AccountsPoolingService.execute(uid)
            except Exception as e:
                logger.error(
                    f"Could not process entry {uid} on account pooling, reason: {e} ")