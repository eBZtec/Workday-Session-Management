from src.connections.database_manager import DatabaseManager
from src.config.wsm_logger import logger
from src.config import config
from src.models.models import Client

class OnlineHostsInfoService:

    async def get_all_hosts_info() -> Client:
        try:
            databaseManager = DatabaseManager()
            all_hosts_info = databaseManager.get_all_sessions_client_info()
            return all_hosts_info
        except KeyError:
            logger.error(f"Not found informations for hostnames into database.")
            return None  # Ou lançar uma exceção específica
        except ConnectionError:
            logger.error("Database connection error while fetching session.")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error in get_all_host_info: {str(e)}")
            return None
        
    async def get_host_info(hostname:str) -> Client:
        try:
            databaseManager = DatabaseManager()
            return databaseManager.get_client_info_by_hostname(hostname)
        except KeyError:
            logger.error(f"Client info not found in for hostname: {hostname}.")
            return None  # Ou lançar uma exceção específica
        except ConnectionError:
            logger.error("Database connection error while fetching for Client informations.")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error in get_client_info_by_hostname: {str(e)}")
            return None