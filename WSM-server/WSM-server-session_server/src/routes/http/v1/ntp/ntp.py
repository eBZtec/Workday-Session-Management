from fastapi import APIRouter, status
from src.controllers.ntp.ntp_action_controller import NTPActionController
from src.models.schema.request_models import NTP_response, StandardWorkHoursSchema
from typing import List

router= APIRouter()

@router.get(
    "/{uid}",
    status_code=status.HTTP_200_OK
)
async def search_ntp_info_by_uid(uid: str) -> List [NTP_response] | None:
    return await NTPActionController().execute(uid)