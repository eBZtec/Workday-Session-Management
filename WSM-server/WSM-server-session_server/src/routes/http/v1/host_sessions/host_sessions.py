from fastapi import APIRouter, status, Query
from src.controllers.host_sessions.host_session_controller import UserSessionController
from src.models.schema.request_models import HostnameSessions
from typing import List, Optional

router = APIRouter()

@router.get(
    "/",
    status_code=status.HTTP_200_OK
)

async def search_user_x_sessions(hostname: Optional[str]= Query(default=None)) -> List [HostnameSessions] | None:
    return await UserSessionController().execute(hostname)