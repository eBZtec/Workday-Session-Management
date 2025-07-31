
from datetime import datetime, date
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy import create_engine
from contextlib import contextmanager
from src.models.models import Base
from src.config import config
from src.utils.filter_transform import paginate_query


# Carregar as variáveis do arquivo .env
load_dotenv()


class SessionDatabaseManager:
    def __init__(self):
        """
        Inicializa o gerenciador do banco de dados.
        """
        database_url = config.SESSION_DATABASE_URL
        self.engine = create_engine(database_url, echo=True)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        if not database_url:
            raise ValueError("DATABASE_URL não encontrada nas variáveis de ambiente.")

    def create_tables(self):
        """
        Cria todas as tabelas no banco de dados, se elas não existirem.
        """
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        """
        Remove todas as tabelas do banco de dados.
        """
        Base.metadata.drop_all(self.engine)

    @contextmanager
    def session_scope(self):
        """
        Fornece um escopo de sessão para transações seguras.
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            session.close()
            raise e
        finally:
            session.close()

    def add_entry(self, entry):
        with self.session_scope() as session:
            session.add(entry)

    def get_all(self, model):
        with self.session_scope() as session:
            return session.query(model).all()

    def get_by_id(self, model, id_):
        with self.session_scope() as session:
            return session.query(model).get(id_)

    def delete_entry(self, model, id_):
        with self.session_scope() as session:
            entry = session.query(model).get(id_)
            if entry:
                session.delete(entry)

    def update_entry(self, model, id_, update_data):
        with self.session_scope() as session:
            entry = session.query(model).get(id_)
            if entry:
                for key, value in update_data.items():
                    setattr(entry, key, value)
