from fastapi import APIRouter, BackgroundTasks
from fastapi import APIRouter, status, Depends
from src.services.auth_service import AuthService

from src.controllers.active_directory.active_diretory_controller import ActiveDirectoryController


auth_service = AuthService()

router = APIRouter(dependencies=[Depends(auth_service.get_current_user)])


@router.post("/enable/{uid}")
async def enable(background_task: BackgroundTasks, uid: str):
    background_task.add_task(ActiveDirectoryController.enable, uid)


@router.post("/disable/{uid}")
async def disable(background_task: BackgroundTasks, uid: str):
    background_task.add_task(ActiveDirectoryController.disable, uid)
