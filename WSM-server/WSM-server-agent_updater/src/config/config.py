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

if not DATABASE_URL:
    raise ValueError("A variável de ambiente DATABASE_URL não está definida.")

if not MQ_ADDRESS_HOST:
    raise ValueError("A variável de ambiente DEV_MQ_ADDRESS_HOST não está definida.")