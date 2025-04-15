import os
import logging
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

# Configurações gerais
DATABASE_URL = os.getenv("DATABASE_URL")
MQ_ADDRESS_HOST = os.getenv("MQ_ADDRESS_HOST")
MQ_HOST_PORT = os.getenv("MQ_HOST_PORT")
MQ_USER = os.getenv("MQ_USER")
MQ_PASSWORD = os.getenv("MQ_PASSWORD")
WORK_HOURS_QUEUE= os.getenv('WORK_HOURS_QUEUE')
LOGOFF_QUEUE = "logoff"
WSM_AGENT_NOTIFICATION_QUEUE = os.getenv('WSM_AGENT_NOTIFICATION_QUEUE')
WSM_FLEXTIME_GRACE_TIME_LOGIN_IN_MINUTES = os.getenv('WSM_FLEXTIME_GRACE_TIME_LOGIN_IN_MINUTES')
WSM_FLEX_HOURS_UPDATER_QUEUE = os.getenv('WSM_FLEXTIME_HOURS_QUEUE')

OAUTH_SECRET_KEY = os.getenv("OAUTH_VALID_SECRET_KEY")

LOG_FILE = os.getenv("WSM_LOG_PATH")
LOG_LOGGER = "WSM Logger"
LOG_LEVEL = logging.DEBUG
LOG_MAX_BYTES = 100*1024*1024
LOG_BACKUP_COUNT = 14

if not DATABASE_URL:
    raise ValueError("A variável de ambiente DATABASE_URL não está definida.")