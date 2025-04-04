from fastapi import HTTPException, status

from src.config.wsm_logger import logger
from src.services.account.presenter.search_account_by_uid_service import SearchAccountByUIDService
from src.services.overtime.get_overtimes_by_account_uid_service import GetOvertimesByAccountUidService
from src.services.targets.get_target_status_by_account_uid_service import GetTargetStatusByAccountUidService


class SearchAccountByUidController:

    @staticmethod
    async def execute(uid: str):
        try:
            account = await SearchAccountByUIDService.execute(uid)

            if account:
                account_overtimes = GetOvertimesByAccountUidService.execute(uid)
                account_target_status_response = await GetTargetStatusByAccountUidService.execute(account.id)

                clean_account_data = dict(account.__dict__)
                clean_account_data.pop('_sa_instance_state', None)

                overtimes = {"overtimes": account_overtimes}
                clean_account_data.update(overtimes)

                if account_target_status_response:
                    targets = []
                    for target_response in account_target_status_response:
                        target, account_target_status = target_response
                        target_status_response = {
                            "target": target.target,
                            "update_timestamp": account_target_status.update_timestamp
                        }
                        targets.append(target_status_response)

                    account_targets = {"target_status": targets}

                    clean_account_data.update(account_targets)

                return clean_account_data
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Account \"{uid}\" not found"
                )
        except Exception as e:
            logger.error(f"Could not search account \"{uid}\", reason: {e}")
            raise e