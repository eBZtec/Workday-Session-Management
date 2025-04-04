from fastapi import HTTPException

from src.config.wsm_logger import logger
from src.enums.types import JourneyType
from src.interfaces.account.icreate_account_and_targets import ICreateAccountAndTargets
from src.models.schema.request_models import StandardWorkHoursSchema
from src.services.account.create_account_and_targets_service import CreateAccountAndTargetsService


class CreateAccountAndTargetsFactory:
    @staticmethod
    def create(standard_work_hours: StandardWorkHoursSchema) -> ICreateAccountAndTargets:
        if standard_work_hours.journey == JourneyType.FREE_TIME or standard_work_hours.journey == JourneyType.FIXED_TIME:
            return CreateAccountAndTargetsService()
        else:
            message = f"Journey type {standard_work_hours.journey} is not configured for create account"
            logger.error(message)
            raise HTTPException(status_code=400, detail=message)