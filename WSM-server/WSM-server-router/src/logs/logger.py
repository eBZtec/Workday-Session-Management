import logging
import os
from logging.handlers import TimedRotatingFileHandler

class Logger:
    def __init__(self, log_name='WSM-Router', log_dir='logs', level=logging.INFO, retention_days=7):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(level)

        # Avoid adding duplicate handlers if the logger already has them
        if not self.logger.hasHandlers():
            # Creates the log directory if it doesn't exist
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Configures the TimedRotatingFileHandler for general logging
            log_file = os.path.join(log_dir, f"{log_name}.log")
            file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=retention_days)
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))

            # StreamHandler to display logs on the console
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(
                '%(levelname)s - %(message)s'
            ))

            # Adds handlers to the logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(stream_handler)

    def get_logger(self):
        """
        Returns the configured logger.
        """
        return self.logger
