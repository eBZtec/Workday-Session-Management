import os
import logging
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

# Configurações gerais
DATABASE_URL = os.getenv("DEV_DATABASE_URL")
MQ_ADDRESS_HOST = os.getenv("DEV_MQ_ADDRESS_HOST")
MQ_HOST_PORT = os.getenv("DEV_MQ_HOST_PORT")
WORK_HOURS_QUEUE= os.getenv('DEV_WORK_HOURS_QUEUE')
LOGOFF_QUEUE = "logoff"
WSM_AGENT_NOTIFICATION_QUEUE = os.getenv('WSM_AGENT_NOTIFICATION_QUEUE')

ZEROMQ_URL = os.getenv("DEV_ZEROMQ_URL")

OAUTH_SECRET_KEY = os.getenv("OAUTH_VALID_SECRET_KEY")

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

if not DATABASE_URL:
    raise ValueError("A variável de ambiente DATABASE_URL não está definida.")







