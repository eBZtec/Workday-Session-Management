from fastapi import HTTPException

from src.config.wsm_logger import logger
from src.enums.types import JourneyType
from src.models.dto.account_dto import AccountDTO
from src.services.account.manager.fixed_work_time_manager import FixedWorkTimeManager
from src.services.account.manager.flex_work_time_manager import FlexWorkTimeManager
from src.services.account.manager.free_work_time_manager import FreeWorkTimeManager
from src.services.account.manager.work_time_manager import WorkTimeManager


class WorkTimeManagerFactory:
    @staticmethod
    def create(account: AccountDTO) -> WorkTimeManager:
        if account.journey == JourneyType.FREE_TIME:
            return FreeWorkTimeManager()
        elif account.journey == JourneyType.FLEX_TIME:
            return FlexWorkTimeManager()
        elif account.journey == JourneyType.FIXED_TIME:
            return FixedWorkTimeManager()
        else:
            message = f"Journey type {account.journey} is not configured for create account"
            logger.error(message)
            raise HTTPException(status_code=400, detail=message)