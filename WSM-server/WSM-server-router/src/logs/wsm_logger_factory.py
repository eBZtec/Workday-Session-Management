import os
import sys
import logging
import logging.handlers
from src.config import config

class LoggerFactory:
    @staticmethod
    def create_logger(name: str = None) -> logging.Logger:
        logger_name = name or config.LOG_NAME
        logger = logging.getLogger(logger_name)
        logger.setLevel(config.LOG_LEVEL)

        if logger.handlers:
            return logger

        formatter = logging.Formatter(config.LOG_FORMAT)

        destinations = config.LOG_DESTINATION.lower()
        valid_options = {"file", "journal"}
        if destinations not in valid_options:
            raise ValueError(f"Invalid log destination: {destinations}. Use file or journal.")

        if destinations in ("file"):
            os.makedirs(config.LOG_DIR, exist_ok=True)
            log_path = os.path.join(config.LOG_DIR, config.LOG_FILENAME)
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=config.LOG_MAX_BYTES,
                backupCount=config.LOG_BACKUP_COUNT
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(config.LOG_LEVEL)
            logger.addHandler(file_handler)

        if destinations in ("journal"):
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)
            stream_handler.setLevel(config.LOG_LEVEL)
            logger.addHandler(stream_handler)

        return logger