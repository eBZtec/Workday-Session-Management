from src.config.wsm_logger import logger
from src.connections.database_manager import DatabaseManager
from src.models.models import StandardWorkHours


class AccountLockManager:

    @staticmethod
    async def lock(uid: str):
        logger.info(f"Starting process to lock account {uid}")
        database_manager = DatabaseManager()

        account: StandardWorkHours | None = database_manager.get_by_uid(StandardWorkHours, uid)

        if account:
            logger.info(f"Found account {account.uid} for locking")
            entry = {"lock": True}
            database_manager.update_entry(StandardWorkHours, account.id, entry)
        else:
            logger.warn(f"Account {uid} not found for lock user")
        logger.info(f"Finishing process to lock account {uid}")

    @staticmethod
    async def unlock(uid: str):
        logger.info(f"Starting process to unlock account {uid}")
        database_manager = DatabaseManager()

        account: StandardWorkHours | None = database_manager.get_by_uid(StandardWorkHours, uid)

        if account:
            logger.info(f"Found account {account.uid} for unlocking")
            entry = {"lock": False}
            database_manager.update_entry(StandardWorkHours, account.id, entry)
        else:
            logger.warn(f"Account {uid} not found for lock user")
        logger.info(f"Finishing process to unlock account {uid}")