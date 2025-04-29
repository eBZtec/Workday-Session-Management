from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from src.config.wsm_logger import logger
from src.controllers.agent.agent_action_controller import AgentActionController
from src.models.schema.agent_model import AgentActionSchema
from src.models.schema.request_models import AccountDisableSchema
from src.services.account.status.account_status_manager import AccountStatusManager
from src.services.pooling.accounts_pooling_service import AccountsPoolingService


class DisableAccountController:

    @staticmethod
    async def execute(uid: str, disable_data: AccountDisableSchema, scheduler: AsyncIOScheduler):
        try:
            await AccountStatusManager.disable(uid, disable_data.disable_reason)
            logger.info(f"Account \"{uid}\" disabled successfully")
        except Exception as e:
            logger.error(f"Failed to disable account \"{uid}\", reason: {e}")
            return
        else:
            try:
                logger.info(f"Starting process account pooling to update account {uid}")
                await AccountsPoolingService.execute(uid)

                run_time = datetime.now() + timedelta(seconds=disable_data.disable_time_in_seconds)
                run_time_string = run_time.strftime("%d-%m-%Y %H:%M:%S")

                logger.info(f"Send message to notify all user {uid} sessions")
                action = AgentActionSchema(action="notify", user=uid, title=f"Sua sessão será desconectada às {run_time_string}", message=disable_data.disable_reason)
                await AgentActionController.execute(action)

                logger.info(f"Scheduling task for logoff all user {uid} sessions")
                action = AgentActionSchema(action="logoff", user=uid, title="", message="")

                scheduler.add_job(
                    AgentActionController.execute,
                    trigger=DateTrigger(run_date=run_time),
                    args=[action],
                    id=f"task_{action.action}_{run_time}",
                    replace_existing=True,
                )

                logger.info(f"Logoff task scheduled to run at {run_time} for user {uid}")
            except Exception as e:
                logger.error(
                    f"Could not process entry {uid} on account pooling, reason: {e} ")