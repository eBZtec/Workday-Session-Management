import logging.handlers
import os

from src.config.wsm_config import wsm_config
from src.shared.generic.base_logger import BaseLogger


class WSMLogger(BaseLogger):
    def __init__(self):
        self._log_name = wsm_config.log_name
        self._log_dir = wsm_config.log_dir
        self._log_filename = wsm_config.log_filename
        self._log_path = str(os.path.join(self._log_dir, self._log_filename))
        self._log_format = wsm_config.log_format
        self._log_level = wsm_config.log_level
        self._log_max_bytes = wsm_config.log_max_bytes
        self._log_backup_count = wsm_config.log_backup_count
        self._logger = None

        self.create_log_dir_if_not_exists()
        self.create_logger()

    def debug(self, message: str):
        self._logger.debug(message)

    def info(self, message: str):
        self._logger.info(message)

    def warning(self, message: str):
        self._logger.warning(message)

    def error(self, message: str):
        self._logger.error(message)

    def critical(self, message: str):
        self._logger.critical(message)

    def create_log_dir_if_not_exists(self):
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)

    def create_logger(self):
        self._logger = logging.getLogger(self._log_name)
        self._logger.setLevel(self._log_level)
        log_handle = logging.handlers.RotatingFileHandler(
            self._log_path,
            maxBytes=self._log_max_bytes,
            backupCount=self._log_backup_count
        )
        log_handle.setLevel(self._log_level)
        log_format = logging.Formatter(self._log_format)
        log_handle.setFormatter(log_format)
        self._logger.addHandler(log_handle)


wsm_logger = WSMLogger()