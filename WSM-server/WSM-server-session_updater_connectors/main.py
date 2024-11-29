import json
import pika
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from src.models.models import Target
from src.config import config
from src.connections.database_manager import DatabaseManager
from src.services.rabbit_manager_service import RabbitMQManagerService
from src.services.message_processor import MessageProcessor
from src.logs.logger import Logger

# RabbitMQ configs
RABBITMQ_HOST = config.RABBITMQ_HOST
RABBITMQ_QUEUE_IN = config.RABBITMQ_QUEUE_IN

# DB Configs
DB_URI = config.DB_URI
logger = Logger(log_name="main").get_logger()

def main():
    try:
        logger.info("WSM - Main - Application started.")
        db_manager = DatabaseManager(DB_URI)
        rabbit_manager = RabbitMQManagerService(RABBITMQ_HOST)
        rabbit_manager.declare_queue(RABBITMQ_QUEUE_IN)

        # Inicializa o processador de mensagens
        processor = MessageProcessor(db_manager, rabbit_manager, RABBITMQ_QUEUE_IN)
        processor.process_messages()
    except Exception as e:
        logger.error(f"WSM - Main - Unhandled error in main: {e}")
    finally:
        rabbit_manager.close()
        logger.info("WSM - Main - Application terminated.")

if __name__ == "__main__":
    main()