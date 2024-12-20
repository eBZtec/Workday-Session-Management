import os
import logging.handlers

from src.config import config


cwd = os.path.dirname(os.path.abspath(__file__))
log_file = config.LOG_FILE
logger = logging.getLogger(config.LOG_LOGGER)
logger.setLevel(config.LOG_LEVEL)
log_handle = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=config.LOG_MAX_BYTES,
    backupCount=config.LOG_BACKUP_COUNT
)
log_handle.setLevel(config.LOG_LEVEL)
log_format = logging.Formatter('%(asctime)s - %(levelname)s - Work Session Management - %(message)s')
log_handle.setFormatter(log_format)
logger.addHandler(log_handle)

