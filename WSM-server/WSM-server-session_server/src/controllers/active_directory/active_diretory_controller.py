from src.config.wsm_logger import logger
from src.services.account.active_directory.active_directory_account_status_manager import \
    ActiveDirectoryAccountStatusManager
from src.services.pooling.accounts_pooling_service import AccountsPoolingService


class ActiveDirectoryController:
    @staticmethod
    async def enable(uid: str):
        try:
            await ActiveDirectoryAccountStatusManager.enable(uid)
        except Exception as e:
            logger.error(f"Failed to enable Active Directory account \"{uid}\", reason: {e}")
        else:
            try:
                logger.info(f"Starting process account pooling to update account {uid}")
                await AccountsPoolingService.execute(uid)
            except Exception as e:
                logger.error(
                    f"Could not process entry {uid} on account pooling, reason: {e} ")

    @staticmethod
    async def disable(uid: str):
        try:
            await ActiveDirectoryAccountStatusManager.disable(uid)
        except Exception as e:
            logger.error(f"Failed to disable Active Directory account \"{uid}\", reason: {e}")
        else:
            try:
                logger.info(f"Starting process account pooling to update account {uid}")
                await AccountsPoolingService.execute(uid)
            except Exception as e:
                logger.error(
                    f"Could not process entry {uid} on account pooling, reason: {e} ")