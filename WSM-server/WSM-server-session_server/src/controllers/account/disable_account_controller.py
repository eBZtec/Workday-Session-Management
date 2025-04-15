from src.config.wsm_logger import logger
from src.controllers.agent.agent_action_controller import AgentActionController
from src.models.schema.agent_model import AgentActionSchema
from src.services.account.status.account_status_manager import AccountStatusManager
from src.services.pooling.accounts_pooling_service import AccountsPoolingService


class DisableAccountController:

    @staticmethod
    async def execute(uid: str):
        try:
            await AccountStatusManager.disable(uid)
            logger.info(f"Account \"{uid}\" disabled successfully")
        except Exception as e:
            logger.error(f"Failed to disable account \"{uid}\", reason: {e}")
            return
        else:
            try:
                logger.info(f"Starting process account pooling to update account {uid}")
                await AccountsPoolingService.execute(uid)

                logger.info(f"Sending message for logoff all user {uid} sessions")
                action = AgentActionSchema(action="logoff", user=uid, title="", message="")
                await AgentActionController.execute(action)
                logger.info(f"Message {action.model_dump()} sent successfully")
            except Exception as e:
                logger.error(
                    f"Could not process entry {uid} on account pooling, reason: {e} ")