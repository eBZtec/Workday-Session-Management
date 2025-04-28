from fastapi import APIRouter

from src.controllers.configuration.configuration_manager_controller import ConfigurationManagerController
from src.models.schema.request_models import ConfigurationRequest

router = APIRouter()


@router.put("/")
async def action(config: ConfigurationRequest):
    await ConfigurationManagerController.update(config)