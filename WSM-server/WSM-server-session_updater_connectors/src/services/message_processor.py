import json
from src.logs.logger import logger
from src.config import config

class MessageProcessor:
    def __init__(self, db_manager, rabbit_manager, input_queue):
        try:
            self.db_manager = db_manager
            self.rabbit_manager = rabbit_manager
            self.input_queue = input_queue
            if not hasattr(rabbit_manager, "consume_messages"):
                raise AttributeError("rabbit_manager não possui o método consume_messages.")
            logger.info("WSM - Session Updater Connectors - MessageProcessor initialized successfully.")
        except Exception as e:
            logger.error(f"WSM - Session Updater Connectors - Message Processor Service - Error initializing MessageProcessor: {e}")
            raise

    def process_messages(self):
        """
        Reprocess messages of entry queue and resent to correspondent queue
        """
        logger.info(f"WSM - Session Updater Connectors - Listening for messages in queue: {self.input_queue}")

        try:
            # Define the callback that will be called for each received message
            def callback(ch, method, properties, body):
                try:
                    self.process_message(body)
                except Exception as e:
                    logger.error(f"Error processing mensage: {e}")
            
            self.rabbit_manager.consume_messages(self.input_queue,callback)

        except KeyboardInterrupt:
            logger.info("WSM - Session Updater Connectors - Message processing interrupted by user.")
        except Exception as e:
            logger.error(f"WSM - Session Updater Connectors - Error in process_messages: {e}")
            raise

   
    def process_message(self, body):
        """
        Processa uma única mensagem.
        """
        try:
            # Parse do JSON recebido
            message = json.loads(body)
            logger.info(f"WSM - Session Updater Connectors - Processing message: {message}")
            target_queue = None
            # Obter o nome da fila com base no serviço
            if "uid" in message:
                uid = message["uid"]
                target_queue = self.db_manager.fetch_target_queue_by_user_uid(uid)
            else:
                uid = message["user"] # direct messages use "user" to refer a user himself 
                target_queue = [config.RABBITMQ_SESSION_AGENT_QUEUE_NAME]
            

            if not target_queue:
                logger.warning(f"WSM - Session Updater Connectors - No target queue for user {uid}. Message skipped.")
                return

            # Resent a message to properly target queues
            self.rabbit_manager.send_message(target_queue, message)

            # When target was updated this sent a msg to agent updater to update windows agent (router -> agent windows) 
            payload = {
                "action":"updateHours",
                "user": uid,
                "message": "",
                "title": ""
            }
            session_agent = ['session_agent']
            a =1  
            self.rabbit_manager.send_message(session_agent, payload)

        except Exception as e:
            logger.error(f"WSM - Session Updater Connectors - Error processing message: {e}")
            raise