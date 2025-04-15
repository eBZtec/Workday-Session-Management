from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.wsm_config import wsm_config
from src.shared.generic.singleton import Singleton


class WSMSessionDatabase(metaclass=Singleton):
    def __init__(self):
        self._session = None
        self.init_connection()

    def init_connection(self):
        engine = create_engine(wsm_config.wsm_session_db_url, echo=False)
        self._session = sessionmaker(bind=engine, expire_on_commit=False)

    @contextmanager
    def session_scope(self):
        """
        Fornece um escopo de sessão para transações seguras.

        Uso:
            with db_manager.session_scope() as session:
                # Realizar operações com a sessão
        """
        session = self._session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            session.close()
            raise e
        finally:
            session.close()

wsm_session_database = WSMSessionDatabase()
        