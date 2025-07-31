from fastapi import APIRouter, status, Query, Path, Depends
from src.controllers.online_hosts_info.online_hosts_info_controller import OnlineHostInfoController
from src.models.schema.request_models import OnlineHostInfoResponse, SessionsSchema
from typing import List, Optional
from src.services.auth_service import AuthService

auth_service = AuthService()

router= APIRouter(dependencies=[Depends(auth_service.get_current_user)])

@router.get("/info/")
async def search_online_host_info(
    hostname: Optional[str] = Query(default=None)
) -> List[OnlineHostInfoResponse] | None:
    return await OnlineHostInfoController().execute(hostname)