import json
from src.services.audit_database_manager import AuditDatabaseManager
from src.models.models import SessionsAudit
from src.services.queue_consumer import QueueConsumer
from src.config.wsm_logger import logger

class AuditService:
    def __init__(self, db_manager: AuditDatabaseManager, queue_consumer: QueueConsumer):
        self.db_manager = db_manager
        self.queue_consumer = queue_consumer

    def process_message(self, ch, method, properties, body):
        print(f"Mensagem recebida: {body}")
        try:
            message = json.loads(body)
            table_name = message.get("table")
            data = message.get("data")
            if not table_name or not data:
                raise ValueError(" Audit Service - Invalid Message. Waiting for: {'table': 'table_name', 'data': {...}}")
            audit_entry = SessionsAudit(**data)
            self.db_manager.add_entry(audit_entry)
        except Exception as e:
            logger.error(f"Audit Service - Error when trying to proccess message: ")
            print(f"Erro ao processar a mensagem: {e}")
        finally:
            self.queue_consumer.acknowledge_message(method.delivery_tag)

    def start(self):
        self.queue_consumer.start_consuming(self.process_message)
