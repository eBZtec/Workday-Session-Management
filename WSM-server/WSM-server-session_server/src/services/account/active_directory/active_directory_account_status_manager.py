from src.config.wsm_logger import logger
from src.connections.database_manager import DatabaseManager
from src.models.models import StandardWorkHours


class ActiveDirectoryAccountStatusManager:

    @staticmethod
    async def enable(uid: str):
        logger.info(f"Starting process to enable Active Directory account {uid}")
        database_manager = DatabaseManager()

        account: StandardWorkHours | None = database_manager.get_by_uid(StandardWorkHours, uid)

        if account:
            logger.info(f"Found account {account.uid} for locking")
            entry = {"active_directory_account_status": True}
            database_manager.update_entry(StandardWorkHours, account.id, entry)
        else:
            logger.warn(f"Account {uid} not found for lock user")
        logger.info(f"Finishing process to enable Active Directory account {uid}")

    @staticmethod
    async def disable(uid: str):
        logger.info(f"Starting process to disable Active Directory account {uid}")
        database_manager = DatabaseManager()

        account: StandardWorkHours | None = database_manager.get_by_uid(StandardWorkHours, uid)

        if account:
            logger.info(f"Found account {account.uid} for locking")
            entry = {"active_directory_account_status": False}
            database_manager.update_entry(StandardWorkHours, account.id, entry)
        else:
            logger.warn(f"Account {uid} not found for lock user")
        logger.info(f"Finishing process to disable Active Directory account {uid}")