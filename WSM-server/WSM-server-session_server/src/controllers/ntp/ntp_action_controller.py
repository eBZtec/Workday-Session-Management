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

    async def execute(self, uid: str):
        try:
            ntp_time = ntpTimeService.get_ntp_time()
            if ntp_time is None:
                logger.error(f"NTP time is None (uid: {uid})")
                raise HTTPException(status_code=500, detail="NTP time could not be retrieved")

            responses = []

            # Caso uid seja None ou string vazia
            if not uid:
                responses.append(NTP_response(
                    uid="N/A",
                    ntp=str(ntp_time),
                    timezone="UTC",
                    tz_name="UTC"
                ))
                return responses

            user_sessions = await TimestampService.user_timestamp(uid)

            for session in user_sessions:
                tz_name, timezone = await self.get_timezone_from_create_timestamp(session.create_timestamp)
                responses.append(NTP_response(
                    uid=str(session.user),
                    ntp=str(ntp_time),
                    timezone=str(timezone) if timezone else "Unknown",
                    tz_name=tz_name if tz_name else "Unknown"
                ))

            return responses

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Unexpected error while retrieving NTP time for uid {uid}: {e}")
            raise HTTPException(status_code=500, detail="Unexpected error occurred")

    async def get_timezone_from_create_timestamp(self, timestamp):
        try:
            dt = datetime.fromisoformat(str(timestamp))
            tz_offset = dt.utcoffset() if dt.tzinfo else None

            if tz_offset is not None:
                offset_hours = tz_offset.total_seconds() / 3600
                for tz_name in pytz.all_timezones:
                    tz = pytz.timezone(tz_name)
                    if dt.astimezone(tz).utcoffset().total_seconds() / 3600 == offset_hours:
                        return tz_name, tz_offset
            return None, tz_offset
        except Exception as e:
            logger.warning(f"Failed to determine timezone from timestamp '{timestamp}': {e}")
            return None, None