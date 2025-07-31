from fastapi import APIRouter, status, Query, Depends
from src.controllers.host_sessions.host_session_controller import UserSessionController
from src.models.schema.request_models import HostnameSessions
from src.services.auth_service import AuthService
from typing import List, Optional

auth_service = AuthService()

router = APIRouter(dependencies=[Depends(auth_service.get_current_user)])

@router.get(
    "/",
    status_code=status.HTTP_200_OK
)

async def search_user_x_sessions(hostname: Optional[str]= Query(default=None)) -> List [HostnameSessions] | None:
    return await UserSessionController().execute(hostname)