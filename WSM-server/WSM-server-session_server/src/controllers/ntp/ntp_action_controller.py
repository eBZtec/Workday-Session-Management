from fastapi import HTTPException, status
from src.config import config
from src.services.ntp.ntp_time_service import ntpTimeService
from src.services.ntp.timestamp_service import TimestampService
from src.config.wsm_logger import logger
from src.models.schema.request_models import NTP_response
from src.models.models import StandardWorkHours
from typing import Optional
from datetime import datetime, timezone
import pytz
import json


class NTPActionController:

    async def execute(self,uid: str ):
        try:
            ntp_time = ntpTimeService.get_ntp_time()
            if ntp_time is None:
                logger.error(f"NTP time is None for uid {uid}")
                return json.dumps({"Error": f"NTP time retrieval failed, NTP time is None for uid: {uid}"})
            user_sessions = await TimestampService.user_timestamp(uid)
            responses = []
            for session in user_sessions:
                tz_name, timezone = await self.get_timezone_from_create_timestamp(session.create_timestamp)
                # Construindo a resposta
                responses.append(NTP_response(
                    uid=str(session.user),
                    ntp=str(ntp_time),
                    timezone=str(timezone),
                    tz_name = tz_name
                ))
            return responses
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Unexpected error while retrieving NTP time for uid {uid}: {e}")
            raise HTTPException(status_code=500, detail="Unexpected error occurred")


    async def get_timezone_from_create_timestamp(self,timestamp):
        timestamp = str(timestamp)
        dt = datetime.fromisoformat(timestamp)

        tz_offset = dt.utcoffset() if dt.tzinfo else None

        if tz_offset is not None:
            offset_hours = tz_offset.total_seconds() / 3600
            for tz_name in pytz.all_timezones:
                tz = pytz.timezone(tz_name)
                if dt.astimezone(tz).utcoffset().total_seconds() / 3600 == offset_hours:
                    return tz_name, tz_offset
        return None, tz_offset
