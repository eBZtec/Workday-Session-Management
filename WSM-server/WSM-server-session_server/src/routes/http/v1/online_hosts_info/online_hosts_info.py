from fastapi import APIRouter, status, Query, Path
from src.controllers.online_hosts_info.online_hosts_info_controller import OnlineHostInfoController
from src.models.schema.request_models import OnlineHostInfoResponse, SessionsSchema
from typing import List, Optional


router= APIRouter()

@router.get("/info/")
async def search_online_host_info(
    hostname: Optional[str] = Query(default=None)
) -> List[OnlineHostInfoResponse] | None:
    return await OnlineHostInfoController().execute(hostname)