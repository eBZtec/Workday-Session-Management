from fastapi import APIRouter, status, Query, Depends
from src.controllers.ntp.ntp_action_controller import NTPActionController
from src.models.schema.request_models import NTP_response, LocationRequest
from src.services.auth_service import AuthService
from typing import List, Optional

auth_service = AuthService()

router= APIRouter(dependencies=[Depends(auth_service.get_current_user)])

@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=NTP_response
)

async def search_ntp_info_by_location(location: LocationRequest):
    return await NTPActionController().execute(location)