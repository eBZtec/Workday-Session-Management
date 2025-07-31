from fastapi import APIRouter, Depends

from src.controllers.configuration.configuration_manager_controller import ConfigurationManagerController
from src.models.schema.request_models import ConfigurationRequest
from src.services.auth_service import AuthService

auth_service = AuthService()

router = APIRouter(dependencies=[Depends(auth_service.get_current_user)])


@router.put("/")
async def action(config: ConfigurationRequest):
    await ConfigurationManagerController.update(config)