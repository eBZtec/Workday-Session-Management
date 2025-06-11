from dotenv import load_dotenv
import os

# Carregar as variáveis do arquivo .env
load_dotenv()

# Configurações gerais
DATABASE_URL = os.getenv("DEV_DATABASE_URL")
MQ_ADDRESS_HOST = os.getenv("DEV_MQ_ADDRESS_HOST")
MQ_HOST_PORT = os.getenv("DEV_MQ_HOST_PORT")
MQ_AGENT_UPDATER_QUEUE = os.getenv("MQ_AGENT_UPDATER_QUEUE")
Z_MQ_PORT= os.getenv("Z_MQ_PORT")
ZEROMQ_URL = os.getenv("DEV_ZEROMQ_URL")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PWD = os.getenv("RABBITMQ_PWD")

LOG_NAME = os.getenv("LOG_NAME")
LOG_LEVEL = os.getenv("LOG_LEVEL")
LOG_FORMAT = os.getenv("LOG_FORMAT")
LOG_DESTINATION = os.getenv("LOG_DESTINATION")
LOG_DIR = os.getenv("LOG_DIR")
LOG_FILENAME = os.getenv("LOG_FILENAME")
LOG_MAX_BYTES = os.getenv("LOG_MAX_BYTES")
LOG_BACKUP_COUNT = os.getenv("LOG_BACKUP_COUNT")


if not DATABASE_URL:
    raise ValueError("[WSM - AGENT UPDATER] A variável de ambiente DATABASE_URL não está definida.")

if not MQ_ADDRESS_HOST:
    raise ValueError("[WSM - AGENT UPDATER] A variável de ambiente DEV_MQ_ADDRESS_HOST não está definida.")