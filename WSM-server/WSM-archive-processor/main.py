from src.services.audit_database_manager import AuditDatabaseManager
from src.services.audit_service import AuditService
from src.services.queue_consumer import QueueConsumer
from src.config import config
from src.config.wsm_logger import logger
import time

def main():
    while True:
        try:
            #Initializing components
            db_manager = AuditDatabaseManager()
            queue_consumer = QueueConsumer(config.QUEUE_NAME)
            audit_service = AuditService(db_manager,queue_consumer)
            
            #start audit service
            audit_service.start()
        except Exception as e:
            # Get any exception and register the error
            logger.error(f"An unexpected error occurred: {str(e)}")
            print(f"An unexpected error occurred: {str(e)}")
            time.sleep(5) 

if __name__ == "__main__":
    main()

