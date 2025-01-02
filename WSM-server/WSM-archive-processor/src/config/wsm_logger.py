import os
import logging.handlers

from src.config import config


cwd = os.path.dirname(os.path.abspath(__file__))
log_file = "logs/archive_processor.log"
logger = logging.getLogger(config.LOG_LOGGER)
logger.setLevel(logging.INFO)
log_handle = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=10485760,
    backupCount= 5
)
log_format = logging.Formatter('%(asctime)s - %(levelname)s - Work Session Management - %(message)s')
log_handle.setFormatter(log_format)
logger.addHandler(log_handle)

