from fastapi import HTTPException, status

from src.config.wsm_logger import logger
from src.enums.target_status_type import TargetStatusType
from src.models.models import Target
from src.models.schema.request_models import TargetSchema
from src.services.targets.create_target_service import CreateTargetService
from src.services.targets.enable_or_disable_target_service import EnableOrDisableTargetService
from src.services.targets.search_all_targets_service import SearchAllTargetsService
from src.services.targets.update_target_service import UpdateTargetService


class TargetsController:

    @staticmethod
    async def create(target: TargetSchema):
        try:
            await CreateTargetService.execute(target)
            logger.info(f"Target {target} created successfully")
        except Exception as e:
            message = f"Could not create target {target}, reason {e}"
            logger.error(message)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    @staticmethod
    async def update(target_id: int, target: TargetSchema):
        try:
            await UpdateTargetService.execute(target_id, target)
            logger.info(f"Target {target} created successfully")
        except Exception as e:
            message = f"Could not update target {target}, reason {e}"
            logger.error(message)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    @staticmethod
    async def enable(target_id: int):
        try:
            await EnableOrDisableTargetService.execute(target_id, TargetStatusType.ENABLE.value)
            logger.info(f"Target {target_id} enabled successfully")
        except Exception as e:
            message = f"Could not enable target {target_id}, reason {e}"
            logger.error(message)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    @staticmethod
    async def disable(target_id: int):
        try:
            await EnableOrDisableTargetService.execute(target_id, TargetStatusType.DISABLE.value)
            logger.info(f"Target {target_id} disabled successfully")
        except Exception as e:
            message = f"Could not disable target {target_id}, reason {e}"
            logger.error(message)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    @staticmethod
    async def list() -> list[Target] | None:
        try:
            return await SearchAllTargetsService.execute()
        except Exception as e:
            message = f"Could not search all targets, reason {e}"
            logger.error(message)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )