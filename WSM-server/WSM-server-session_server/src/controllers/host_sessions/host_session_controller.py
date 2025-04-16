from fastapi import HTTPException, status
from src.config import config
from src.services.host_sessions.host_sessions_service import hostSessionService
from src.config.wsm_logger import logger

class UserSessionController:

    async def execute (self,hostname ):
        try:
            responses = []
            if hostname == None:
                all_host_sessions = await hostSessionService.get_all_hosts_sessions()
                
                for session in all_host_sessions:
                    responses.append(session)
            else:
                host_sessions = await hostSessionService.get_host_session(hostname)
                for session in host_sessions:
                    responses.append(session)
            return responses
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Unexpected error while trying to get active sessions: {e}")
            raise HTTPException(status_code=500, detail="Unexpected error occurred")
