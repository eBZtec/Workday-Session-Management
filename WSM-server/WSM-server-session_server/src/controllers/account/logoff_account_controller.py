from src.config.wsm_logger import logger
from src.services.account.logoff_account_zeromq_service import LogoffAccountZeroMQService


class LogoffAccountController:

    @staticmethod
    async def execute(uid: str, host: str):
        try:
            LogoffAccountZeroMQService.logoff(uid, host)
        except Exception as e:
            logger.error(f"Could not logoff account \"{uid}\" from host \"{host}\", reason {e}")