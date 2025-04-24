from src.config.wsm_logger import logger
from src.services.account.status.account_lock_manager import AccountLockManager
from src.services.pooling.accounts_pooling_service import AccountsPoolingService


class LockAccountController:

    @staticmethod
    async def lock(uid: str):
        try:
            await AccountLockManager.lock(uid)
        except Exception as e:
            logger.error(f"Failed to lock account \"{uid}\", reason: {e}")
        else:
            try:
                logger.info(f"Starting process account pooling to update account {uid}")
                await AccountsPoolingService.execute(uid)
            except Exception as e:
                logger.error(
                    f"Could not process entry {uid} on account pooling, reason: {e} ")

    @staticmethod
    async def unlock(uid: str):
        try:
            await AccountLockManager.unlock(uid)
        except Exception as e:
            logger.error(f"Failed to lock account \"{uid}\", reason: {e}")
        else:
            try:
                logger.info(f"Starting process account pooling to update account {uid}")
                await AccountsPoolingService.execute(uid)
            except Exception as e:
                logger.error(
                    f"Could not process entry {uid} on account pooling, reason: {e} ")