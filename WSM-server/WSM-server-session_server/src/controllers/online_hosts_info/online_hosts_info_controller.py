from fastapi import HTTPException, status
from src.config import config
from src.services.online_hosts_info.online_hosts_info_service import OnlineHostsInfoService
from src.config.wsm_logger import logger
from src.models.schema.request_models import OnlineHostInfoResponse
class OnlineHostInfoController:
    

    async def execute(self, hostname):
        try:

            responses = []
            if hostname == None:
                all_hosts_info = await OnlineHostsInfoService.get_all_hosts_info()
                for (hostname,user,ip_address,client_version,os_name,os_version,uptime,agent_info) in all_hosts_info:
                    responses.append(OnlineHostInfoResponse(
                        hostname=hostname,
                        user=user,
                        client_ip_address=ip_address,
                        client_cli_version=client_version,
                        client_os_name=os_name,
                        client_os_version=os_version,
                        client_uptime=uptime,
                        client_agent_info=agent_info,
                    ))

                return responses
            else:
                host_infos  = await OnlineHostsInfoService.get_host_info(hostname)
                for (hostname,user,ip_address,client_version,os_name,os_version,uptime,agent_info) in host_infos:
                    responses.append(OnlineHostInfoResponse(
                        hostname=hostname,
                        user=user,
                        client_ip_address=ip_address,
                        client_cli_version=client_version,
                        client_os_name=os_name,
                        client_os_version=os_version,
                        client_uptime=uptime,
                        client_agent_info=agent_info,
                    ))
            return responses
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Unexpected error while trying to get active hosts infos: {e}")
            raise HTTPException(status_code=500, detail="Unexpected error occurred")
