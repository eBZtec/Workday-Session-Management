from src.config.wsm_logger import logger
from src.models.schema.request_models import ConfigurationRequest
from src.services.configuration.configuration_manager_service import ConfigurationManagerService


class ConfigurationManagerController:

    @staticmethod
    async def update(config: ConfigurationRequest):
        try:
            logger.info("Starting process to update WSM Configuration")
            logger.debug(f"Configuration update data received {config}")

            await ConfigurationManagerService.update(config)
            logger.info("WSM Configuration updated successfully")
        except Exception as e:
            logger.error(f"Could not update WSM configuration, reason: {e}")