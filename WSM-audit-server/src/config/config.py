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

LOG_FILE = "./logs/wsm.log"
LOG_LOGGER = "WSM Logger"
LOG_LEVEL = logging.DEBUG
LOG_MAX_BYTES = 100*1024*1024
LOG_BACKUP_COUNT = 14

if not DATABASE_URL:
    raise ValueError("A variável de ambiente DATABASE_URL não está definida.")







