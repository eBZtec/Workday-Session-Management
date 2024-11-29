from fastapi import HTTPException, status

from src.config.wsm_logger import logger
from src.services.account.search_account_by_uid_service import SearchAccountByUIDService


class SearchAccountByUidController:

    @staticmethod
    async def execute(uid: str):
        try:
            account = await SearchAccountByUIDService.execute(uid)

            if account:
                clean_account_data = dict(account.__dict__)
                clean_account_data.pop('_sa_instance_state', None)
                return clean_account_data
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Account \"{uid}\" not found"
                )
        except Exception as e:
            logger.error(f"Could not search account \"{uid}\", reason: {e}")
            raise e