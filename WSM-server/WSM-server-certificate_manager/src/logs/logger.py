import logging
import os

class Logger:
    def __init__(self, log_name='app', log_dir='logs', level=logging.INFO):
        """
        Initializes the logger, configuring the log directory and handlers.

        :param log_name: Base name for the log file.
        :param log_dir: Directory where logs will be saved.
        :param level: Log level (default: logging.INFO).
        """
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(level)

        # Creates the log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Configures the general log files
        log_file = os.path.join(log_dir, f"{log_name}.log")
        error_log_file = os.path.join(log_dir, "error.log")

        # FileHandler for general logging
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))

        # FileHandler for error logging
        error_handler = logging.FileHandler(error_log_file)
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

        # Adds handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(stream_handler)

    def get_logger(self):
        """
        Returns the configured logger.
        """
        return self.logger
