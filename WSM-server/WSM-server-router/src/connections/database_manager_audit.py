from sqlalchemy import create_engine, or_, select
from sqlalchemy.orm import sessionmaker
from src.models.models import SessionAudit 
from dotenv import load_dotenv
from sqlalchemy import create_engine
from contextlib import contextmanager
from src.models.models import Base
from src.config import config
import os, json

# Carregar as variáveis do arquivo .env
load_dotenv()

class DatabaseManagerAudit:
    def __init__(self):
        """
        Inicializa o gerenciador do banco de dados.

        Args:
            database_url (str): A URL de conexão com o banco de dados.
        """

        database_url = config.DATABASE_URL_AUDIT
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

        Uso:
            with db_manager.session_scope() as session:
                # Realizar operações com a sessão
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Erro durante a transação: {e}")
        finally:
            session.close()

    def add_entry(self, entry):
        """
        Adiciona um novo registro ao banco de dados.

        Args:
            entry (Base): A instância da classe representando a tabela do banco de dados.
        """
        with self.session_scope() as session:
            session.add(entry)

    def get_all(self, model):
        """
        Retorna todos os registros de uma tabela específica.

        Args:
            model (Base): A classe representando a tabela do banco de dados.

        Returns:
            list: Lista de todas as instâncias do modelo.
        """
        with self.session_scope() as session:
            return session.query(model).all()

    def get_by_id(self, model, id_):
        """
        Retorna um registro específico pelo ID.

        Args:
            model (Base): A classe representando a tabela do banco de dados.
            id_ (int): O ID do registro.

        Returns:
            model: Instância da classe correspondente ao registro encontrado.
        """
        with self.session_scope() as session:
            return session.query(model).get(id_)

    def delete_entry(self, model, id_):
        """
        Deleta um registro do banco de dados pelo ID.

        Args:
            model (Base): A classe representando a tabela do banco de dados.
            id_ (int): O ID do registro a ser deletado.
        """
        with self.session_scope() as session:
            entry = session.query(model).get(id_)
            if entry:
                session.delete(entry)

    def update_entry(self, model, id_, update_data):
        """
        Atualiza um registro específico.

        Args:
            model (Base): A classe representando a tabela do banco de dados.
            id_ (int): O ID do registro a ser atualizado.
            update_data (dict): Dicionário contendo os atributos e seus novos valores.
        """
        with self.session_scope() as session:
            entry = session.query(model).get(id_)
            if entry:
                for key, value in update_data.items():
                    setattr(entry, key, value)

######   CUSTOMIZED QUERIES   ###########

    def insert_cleaned_session(self, **kwargs):
        audit_entry = SessionAudit(
            hostname=kwargs["hostname"],
            event_type="logout",
            login=kwargs["login"],
            status="disconnected",
            start_time=kwargs["start_time"],
            end_time=kwargs["end_time"],
            create_timestamp=kwargs["create_timestamp"],
            update_timestamp=kwargs.get("update_timestamp"),
            os_version=kwargs["os_version"],
            os_name=kwargs.get("os_name"),
            ip_address=kwargs["ip_address"],
            client_version=kwargs["client_version"],
            agent_info=kwargs.get("agent_info"),
            audit_source="cleanup_disconected_service"
        )
        self.add_entry(audit_entry)


