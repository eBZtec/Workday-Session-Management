from dotenv import load_dotenv
import os

# Carregar as variáveis do arquivo .env
load_dotenv()

DB_URI= os.getenv("DB_URI")

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')

RABBITMQ_QUEUE_IN = os.getenv("RABBITMQ_QUEUE_IN")

RABBITMQ_SESSION_AGENT_QUEUE_NAME = os.getenv("RABBITMQ_SESSION_AGENT_QUEUE_NAME")