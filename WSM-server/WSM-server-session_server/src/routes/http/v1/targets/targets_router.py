from fastapi import APIRouter

from src.controllers.targets.targets_controller import TargetsController
from src.models.schema.request_models import TargetSchema

router = APIRouter()


@router.post("/")
async def create(target: TargetSchema):
    await TargetsController.create(target)


@router.put("/{target_id}")
async def update(target_id: int, target: TargetSchema):
    await TargetsController.update(target_id, target)


@router.patch("/enable/{target_id}")
async def enable(target_id: int):
    await TargetsController.enable(target_id)


@router.patch("/disable/{target_id}")
async def disable(target_id: int):
    await TargetsController.disable(target_id)


@router.get("/")
async def list_all():
    return await TargetsController.list()

