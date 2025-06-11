from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from src.models.models import Target, TargetStatus, StandardWorkHours
from src.logs.logger import logger


class DatabaseManager:

    def __init__(self, db_uri):
        try:
            self.engine = create_engine(db_uri)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("WSM - Session Updater Connectors - DatabaseManager initialized successfully.")
        except Exception as e:
            logger.error(f"WSM - Session Updater Connectors - Error initializing DatabaseManager: {e}")
            raise


    def fetch_target_queue_by_user_uid(self, _uid):
        """
        Busca a fila correspondente no banco de dados com base no serviço.
        """
        
        try:
            with self.Session() as session:
                query = (select(Target.service)
                         .join(TargetStatus, Target.id == TargetStatus.id_target)
                         .join(StandardWorkHours, StandardWorkHours.id == TargetStatus.std_wrk_id)
                         .where(StandardWorkHours.uid == _uid, Target.enabled == 0)
                         )
                result = session.execute(query).scalars().all()
                if result:
                    logger.info(f"WSM - Session Updater Connectors - Queues fetched for uid {_uid}: {result}")
                else:
                    logger.warning(f"WSM - Session Updater Connectors -No queues found for uid: {_uid}")
                return result
        except Exception as e:
            logger.error(f"WSM - Session Updater Connectors - Error fetching target queue for uid {_uid}: {e}")
            raise
            