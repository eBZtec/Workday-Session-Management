from fastapi import HTTPException, status

from src.config.wsm_logger import logger
from src.models.schema.request_models import ExtendedWorkHoursResponse
from src.services.overtime.get_overtimes_by_account_uid_service import GetOvertimesByAccountUidService


class SearchOvertimeController:

    @staticmethod
    def execute(account_uid: str) -> list[ExtendedWorkHoursResponse]:
        try:
            overtimes = GetOvertimesByAccountUidService.execute(account_uid)
            return overtimes
        except Exception as e:
            logger.error(f"Could not found account overtimes, reason {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not found account overtimes, reason {e}"
            )