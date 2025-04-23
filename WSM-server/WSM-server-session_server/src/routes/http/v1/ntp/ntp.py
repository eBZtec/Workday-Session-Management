from fastapi import APIRouter, status, Query
from src.controllers.ntp.ntp_action_controller import NTPActionController
from src.models.schema.request_models import NTP_response, StandardWorkHoursSchema
from typing import List, Optional

router= APIRouter()

@router.get(
    "/",
    status_code=status.HTTP_200_OK
)

async def search_ntp_info_by_uid(uid: Optional[str] = None) -> Optional [List[NTP_response]]:
    return await NTPActionController().execute(uid)