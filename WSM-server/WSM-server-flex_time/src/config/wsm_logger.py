import logging.handlers
import os
import threading
from src.config.wsm_config import wsm_config
from src.shared.generic.base_logger import BaseLogger
from src.config.wsm_logger_factory import LoggerFactory


class WSMLogger(BaseLogger):
    _instance=None
    _lock=threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(WSMLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Garante que a inicialização só ocorre uma vez
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._logger = LoggerFactory.create_logger()
        self._initialized = True

    def __init__(self):
        self._logger = LoggerFactory.create_logger()

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

logger = WSMLogger()
