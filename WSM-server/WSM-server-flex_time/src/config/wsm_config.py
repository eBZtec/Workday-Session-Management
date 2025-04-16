import os
from threading import Lock
from dotenv import load_dotenv

from src.shared.generic.singleton import Singleton


class SingletonConfig(type):
    _instances = {}

    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls._instances[cls] = super().__call__()
        print(cls._instances)

    def __call__(cls, *args, **kwargs):
        return cls._instances[cls]


class Config(metaclass=Singleton):
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                load_dotenv()  # Load .env only once
                cls._instance._load_env_vars()
            return cls._instance

    def _load_env_vars(self):
        self.log_name = os.getenv("WSM_SERVER_FLEX_TIME_LOG_NAME=")
        self.log_dir = os.getenv("WSM_SERVER_FLEX_TIME_LOG_DIR")
        self.log_filename = os.getenv("WSM_SERVER_FLEX_TIME_LOG_FILENAME")
        self.log_format = os.getenv("WSM_SERVER_FLEX_TIME_LOG_FORMAT")
        self.log_level = int(os.getenv("WSM_SERVER_FLEX_TIME_LOG_LEVEL"))
        self.log_max_bytes = int(os.getenv("WSM_SERVER_FLEX_TIME_LOG_MAX_BYTES"))
        self.log_backup_count = os.getenv("WSM_SERVER_FLEX_TIME_LOG_BACKUP_COUNT")

        self.wsm_session_db_url = os.getenv("DATABASE_URL")

        self.wsm_queue_host = os.getenv("MQ_ADDRESS_HOST")
        self.wsm_queue_port = int(os.getenv("MQ_HOST_PORT"))
        self.wsm_queue_user = os.getenv("MQ_USER")
        self.wsm_queue_user_password = os.getenv("MQ_PASSWORD")
        self.wsm_queue_updater = os.getenv("WSM_SERVER_FLEX_QUEUE_UPDATER")
        self.wsm_queue_pooling = os.getenv("WORK_HOURS_QUEUE")

        self.wsm_zeromq_url = os.getenv("ZEROMQ_URL")


wsm_config = Config()