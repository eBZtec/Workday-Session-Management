import json
from src.logs.logger import Logger
from src.config import config

logger = Logger(log_name='WSM-Server-Agent-Updater').get_logger()

class MessageProcessor:
    def __init__(self, db_manager, rabbit_manager, input_queue):
        try:
            self.db_manager = db_manager
            self.rabbit_manager = rabbit_manager
            self.input_queue = input_queue
            if not hasattr(rabbit_manager, "consume_message"):
                raise AttributeError("rabbit_manager não possui o método consume_message.")
            logger.info("WSM - Session Updater Connectors - MessageProcessor initialized successfully.")
        except Exception as e:
            logger.error(f"WSM - Session Updater Connectors - Message Processor Service - Error initializing MessageProcessor: {e}")
            raise

    def process_messages(self):
        """
        Processa mensagens da fila de entrada e as reenviam para a fila correspondente.
        """
        logger.info(f"WSM - Session Updater COnnectors - Listening for messages in queue: {self.input_queue}")
        try:
            while True:
                body = self.rabbit_manager.consume_message(self.input_queue)
                if body:
                    self.process_message(body)
        except KeyboardInterrupt:
            logger.info("WSM - Session Updater COnnectors - Message processing interrupted by user.")
        except Exception as e:
            logger.error(f"WSM - Session Updater COnnectors - Error in process_messages: {e}")
            raise

    def process_message(self, body):
        """
        Processa uma única mensagem.
        """
        try:
            # Parse do JSON recebido
            message = json.loads(body)
            logger.info(f"WSM - Session Updater COnnectors - Processing message: {message}")
            target_queue = None
            # Obter o nome da fila com base no serviço
            if "uid" in message:
                uid = message["uid"]
                target_queue = self.db_manager.fetch_target_queue_by_user_uid(uid)
            else:
                uid = message["user"] # direct messages use "user" to refer a user himself 
                target_queue = [config.RABBITMQ_SESSION_AGENT_QUEUE_NAME]
            

            if not target_queue:
                logger.warning(f"WSM - Session Updater COnnectors - No target queue for user {uid}. Message skipped.")
                return

            # Reenviar a mensagem para a fila apropriada
            self.rabbit_manager.send_message(target_queue, message)
            
        except Exception as e:
            logger.error(f"WSM - Session Updater COnnectors - Error processing message: {e}")
            raise