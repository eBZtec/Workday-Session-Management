from fastapi import APIRouter, BackgroundTasks

from src.controllers.active_directory.active_diretory_controller import ActiveDirectoryController

router = APIRouter()


@router.post("/enable/{uid}")
async def enable(background_task: BackgroundTasks, uid: str):
    background_task.add_task(ActiveDirectoryController.enable, uid)


@router.post("/disable/{uid}")
async def disable(background_task: BackgroundTasks, uid: str):
    background_task.add_task(ActiveDirectoryController.disable, uid)
