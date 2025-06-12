import os
import sys
import logging
import logging.handlers
from src.config.wsm_config import wsm_config  # <- instância da sua classe Config


class LoggerFactory:
    @staticmethod
    def create_logger(name: str = None) -> logging.Logger:
        logger_name = name or wsm_config.log_name or "default_logger"
        logger = logging.getLogger(logger_name)

        # Converte o nível textual (ex: "DEBUG") para int
        log_level = getattr(logging, str(wsm_config.log_level).upper(), logging.INFO)
        logger.setLevel(log_level)

        if logger.handlers:
            return logger

        formatter = logging.Formatter(wsm_config.log_format)

        destination = (os.getenv("LOG_DESTINATION") or "file").lower()
        valid_options = {"file", "journal", "both"}
        if destination not in valid_options:
            raise ValueError(f"Invalid log destination: {destination}. Use file, journal, or both.")

        if destination in ("file", "both"):
            os.makedirs(wsm_config.log_dir, exist_ok=True)
            log_path = os.path.join(wsm_config.log_dir, wsm_config.log_filename)
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=wsm_config.log_max_bytes,
                backupCount=int(wsm_config.log_backup_count)
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            logger.addHandler(file_handler)

        if destination in ("journal", "both"):
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)
            stream_handler.setLevel(log_level)
            logger.addHandler(stream_handler)

        return logger
