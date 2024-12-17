import logging
import os
from logging.handlers import TimedRotatingFileHandler

class Logger:
    _instance = None  # Singleton instance

    def __new__(cls, log_name='app', log_dir='logs', level=logging.INFO, retention_days=7):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize(log_name, log_dir, level, retention_days)
        return cls._instance

    def _initialize(self, log_name, log_dir, level, retention_days):
        self.logger = logging.getLogger(log_name)
        if not self.logger.hasHandlers():  # Avoid adding handlers multiple times
            self.logger.setLevel(level)

            # Create the log directory if it doesn't exist
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Configure the TimedRotatingFileHandler for general logging
            log_file = os.path.join(log_dir, f"{log_name}.log")
            file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=retention_days)
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))

            # Configure the TimedRotatingFileHandler for error logging
            error_log_file = os.path.join(log_dir, "error.log")
            error_handler = TimedRotatingFileHandler(error_log_file, when="midnight", interval=1, backupCount=retention_days)
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))

            # StreamHandler to display logs on the console
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(
                '%(name)s - %(levelname)s - %(message)s'
            ))

            # Add handlers to the logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(error_handler)
            self.logger.addHandler(stream_handler)

    def get_logger(self):
        return self.logger
