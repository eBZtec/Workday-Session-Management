from dotenv import load_dotenv
import os

# Carregar as variáveis do arquivo .env
load_dotenv()

DB_URI= os.getenv("DB_URI")

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')

RABBITMQ_QUEUE_IN = os.getenv("RABBITMQ_QUEUE_IN")

RABBITMQ_SESSION_AGENT_QUEUE_NAME = os.getenv("RABBITMQ_SESSION_AGENT_QUEUE_NAME")

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

