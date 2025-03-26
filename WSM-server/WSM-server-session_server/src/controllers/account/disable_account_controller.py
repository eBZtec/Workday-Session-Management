from src.config.wsm_logger import logger
from src.controllers.agent.agent_action_controller import AgentActionController
from src.models.schema.agent_model import AgentActionSchema
from src.services.account.enable_or_disable_account_by_uid_service import EnableOrDisableAccountByUidService
from src.services.pooling.accounts_pooling_service import AccountsPoolingService


class DisableAccountController:

    @staticmethod
    async def execute(uid: str):
        try:
            await EnableOrDisableAccountByUidService.execute(uid, False)
            logger.info(f"Account \"{uid}\" disabled successfully")
        except Exception as e:
            logger.error(f"Failed to disable account \"{uid}\", reason: {e}")
        else:
            try:
                logger.info(f"Starting process account pooling to update account {uid}")
                await AccountsPoolingService.execute(uid)
                action = AgentActionSchema(action="logoff", user=uid, title="", message="")
                await AgentActionController.execute(action)
            except Exception as e:
                logger.error(
                    f"Could not process entry {uid} on account pooling, reason: {e} ")