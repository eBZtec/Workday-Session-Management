from src.connections.database_manager import DatabaseManager
from src.models.models import TargetStatus
from src.services.targets.search_enable_targets_service import SearchEnableTargetsService


class ConfigureAccountTargets:

    @staticmethod
    async def execute(account_id: int):
        database_manager = DatabaseManager()
        targets_enable = await SearchEnableTargetsService.execute()

        for target in targets_enable:
            target_id = target.id

            target_status = TargetStatus()
            target_status.std_wrk_id = account_id
            target_status.id_target = target_id

            database_manager.add_entry(target_status)
