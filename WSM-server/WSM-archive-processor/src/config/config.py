import os
from dotenv import load_dotenv


load_dotenv()

AUDIT_DB_URL = os.getenv("AUDIT_DB_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME")
QUEUE_HOST = os.getenv("QUEUE_HOST")



#Logging configuration
LOG_FILE = os.getenv("WSM_LOG_PATH")
LOG_NAME = os.getenv("LOG_NAME")
LOG_LOGGER = "WSM Logger"
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES"))
LOG_BACKUP_COUNT = os.getenv("LOG_BKP_COUNT")
LOG_DIR=os.getenv("LOG_DIR")
LOG_FORMAT=os.getenv("LOG_FORMAT")
LOG_FILENAME=os.getenv("LOG_FILENAME")
LOG_LEVEL=os.getenv("LOG_LEVEL")
LOG_DESTINATION=os.getenv("LOG_DESTINATION")
