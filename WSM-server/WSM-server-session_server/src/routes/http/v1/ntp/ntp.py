from fastapi import APIRouter, status, Query
from src.controllers.ntp.ntp_action_controller import NTPActionController
from src.models.schema.request_models import NTP_response, LocationRequest
from typing import List, Optional

router= APIRouter()

@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=NTP_response
)

async def search_ntp_info_by_location(location: LocationRequest):
    return await NTPActionController().execute(location)