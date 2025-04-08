from dotenv import load_dotenv
import os

# Carregar as variáveis do arquivo .env
load_dotenv()

# Configurações gerais
DATABASE_URL = os.getenv("DEV_DATABASE_URL")
MQ_ADDRESS_HOST = os.getenv("DEV_MQ_ADDRESS_HOST")
MQ_HOST_PORT = os.getenv("DEV_MQ_HOST_PORT")
WORK_HOURS_QUEUE= os.getenv("DEV_WORK_HOURS_QUEUE")
Z_MQ_PORT= os.getenv("Z_MQ_PORT")

ZEROMQ_URL = os.getenv("DEV_ZEROMQ_URL")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_QUEUE= os.getenv("RABBITMQ_QUEUE")

RABBITMQ_USER = os.getenv("RABBITMQ_USER")

RABBITMQ_PWD = os.getenv("RABBITMQ_PWD")

if not DATABASE_URL:
    raise ValueError("A variável de ambiente DATABASE_URL não está definida.")