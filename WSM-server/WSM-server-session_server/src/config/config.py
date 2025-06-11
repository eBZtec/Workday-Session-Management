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
WSM_CONNECTOR_AD_QUEUE_NAME = os.getenv('WSM_CONNECTOR_AD_QUEUE_NAME')
NTP_SERVER= os.getenv('NTP_SERVER')
NTP_PORT = os.getenv('NTP_PORT')
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