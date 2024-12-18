from src.services.audit_database_manager import AuditDatabaseManager
from src.services.audit_service import AuditService
from src.services.queue_consumer import QueueConsumer
from src.config import config

def main():

    db_manager = AuditDatabaseManager()
    queue_consumer = QueueConsumer(config.QUEUE_NAME)

    audit_service = AuditService(db_manager,queue_consumer)

    audit_service.start()


if __name__ == "__main__":
    main()

