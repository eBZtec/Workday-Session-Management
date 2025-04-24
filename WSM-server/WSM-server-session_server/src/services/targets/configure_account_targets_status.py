from src.config.wsm_logger import logger
from src.connections.database_manager import DatabaseManager
from src.models.models import TargetStatus
from src.services.targets.get_target_status_by_account_uid_service import GetTargetStatusByAccountUidService
from src.services.targets.search_enable_targets_service import SearchEnableTargetsService


class ConfigureAccountTargets:

    @staticmethod
    async def execute(account_id: int):
        logger.info(f"Starting process to create account targets for account {account_id}")
        database_manager = DatabaseManager()
        targets_enable = await SearchEnableTargetsService.execute()
        user_current_targets = await GetTargetStatusByAccountUidService.execute(account_id)

        for target in targets_enable:
            target_id = target.id

            add_target = True

            for user_current_target in user_current_targets:
                target_teste, account_target_status = user_current_target
                if account_target_status.id_target == target_id:
                    add_target = False
                    break

            if add_target:
                target_status = TargetStatus()
                target_status.std_wrk_id = account_id
                target_status.id_target = target_id

                logger.info(f"Adding target id {target.target} for account {account_id}")

                database_manager.add_entry(target_status)
            else:
                logger.info(f"Target id {target.target} already exists for account {account_id}. Skipping...")