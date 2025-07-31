from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, status, Depends, BackgroundTasks, Query
from starlette.status import HTTP_200_OK

from src.connections.scheduler import get_scheduler
from src.controllers.account.lock_account_controller import LockAccountController
from src.controllers.account.search_account_by_uid_controller import SearchAccountByUidController
from src.models.dto.account_dto import AccountDTO
from src.services.account.presenter.search_flex_time_presenter import SearchFlexTimePresenter
from src.services.auth_service import AuthService
from src.models.schema.request_models import StandardWorkHoursResponse, FlexTimeResponse, \
    AccountDisableSchema
from src.controllers.account.disable_account_controller import DisableAccountController
from src.controllers.account.enable_account_controller import EnableAccountController
from src.controllers.account.logoff_account_controller import LogoffAccountController
from src.controllers.account.update_account_controller import UpdateAccountController
from src.controllers.account.create_account_controller import CreateAccountController


auth_service = AuthService()

router = APIRouter(dependencies=[Depends(auth_service.get_current_user)])

@router.post(
    "/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def create(
        background_task: BackgroundTasks,
        account: AccountDTO
):
    background_task.add_task(CreateAccountController.execute, account)


@router.put(
    "/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def update(
        background_task: BackgroundTasks,
        account: AccountDTO
):
    background_task.add_task(UpdateAccountController.execute, account)


@router.post(
    "/{uid}/disable",
    status_code=status.HTTP_204_NO_CONTENT
)
async def deactivate(
        background_task: BackgroundTasks,
        uid: str,
        disable_data: AccountDisableSchema,
        scheduler = Depends(get_scheduler)
):
    background_task.add_task(DisableAccountController.execute, uid, disable_data, scheduler)


@router.post(
    "/{uid}/enable",
    status_code=status.HTTP_204_NO_CONTENT
)
async def enable(background_task: BackgroundTasks, uid: str):
    background_task.add_task(EnableAccountController.execute, uid)


@router.post(
    "/lock/{uid}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def lock(background_task: BackgroundTasks, uid: str):
    background_task.add_task(LockAccountController.lock, uid)


@router.post(
    "/unlock/{uid}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def unlock(background_task: BackgroundTasks, uid: str):
    background_task.add_task(LockAccountController.unlock, uid)


@router.post(
    "/{uid}/logoff/{host}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def logoff(uid: str, host: str):
    await LogoffAccountController.execute(uid, host)


@router.get(
    "/{uid}",
    status_code=status.HTTP_200_OK
)
async def search_account_by_uid(uid: str) -> StandardWorkHoursResponse | None:
    return await SearchAccountByUidController.execute(uid)


@router.get(
    "/flextime/{uid}",
    status_code=HTTP_200_OK,
    name="Search flex times register by user",
    response_model=List[FlexTimeResponse]
)
async def get_flex_times_by_user_and_period(
    uid: str,
    skip: int = 0,
    limit: int = 10,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None)
):
    return SearchFlexTimePresenter.get_flex_time_by_user_and_date(
        uid,
        date_from,
        date_to,
        skip,
        limit
    )