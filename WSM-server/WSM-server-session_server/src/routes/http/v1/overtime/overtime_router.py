from fastapi import APIRouter, status, BackgroundTasks

from src.controllers.overtime.insert_overtime_controller import InsertOvertimeController
from src.controllers.overtime.search_overtime_controller import SearchOvertimeController
from src.controllers.overtime.update_overtime_controller import UpdateOvertimeController
from src.models.schema.request_models import ExtendedWorkHoursSchema, ExtendedWorkHoursResponse

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    name="Insert overtime"
)
async def insert(background_task: BackgroundTasks, overtime: ExtendedWorkHoursSchema):
    background_task.add_task(InsertOvertimeController.execute, overtime)


@router.put(
    "/{overtime_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def update(background_task: BackgroundTasks, overtime_id: int, overtime: ExtendedWorkHoursSchema):
    background_task.add_task(UpdateOvertimeController.execute, overtime_id, overtime)

@router.get(
    "/account/{account_id}"
)
async def get_account_overtimes(account_id: str) -> list[ExtendedWorkHoursResponse] | None:
    return SearchOvertimeController.execute(account_id)

