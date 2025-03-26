from datetime import datetime, date

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy import create_engine
from contextlib import contextmanager
from src.models.models import Base, TargetStatus
from src.config import config
from src.models.models import Holidays, ExtendedWorkHours, Target
import os

# Carregar as variáveis do arquivo .env
load_dotenv()

class DatabaseManager:
    def __init__(self):
        """
        Inicializa o gerenciador do banco de dados.

        Args:
            database_url (str): A URL de conexão com o banco de dados.
        """

        database_url = config.DATABASE_URL
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
            session.close()
            raise e
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

    def get_id_by_uid(self, model,uid_):
        with self.session_scope() as session:
            return session.query(model.id).filter_by(uid=uid_).scalar()


    def get_by_uid(self, model, uid_):
        with self.session_scope() as session:
            return session.query(model).filter_by(uid=uid_).first()
        

    def get_by_employee_id(self,model,employee_id_):
        with self.session_scope() as session:
            return session.query(model).filter_by(employee_id=employee_id_).first()
        

######    CUSTOMIZED PONTUAL QUERIES    ############

    def get_holidays(self, city) -> list[Holidays] | None:
        with self.session_scope() as session:
            return session \
                .query(Holidays) \
                .filter(or_(Holidays.holiday_type.like("N"),Holidays.city == city)) \
                .all()


    def get_active_extensions(self, uid, start_date: datetime, end_date: datetime):
        with self.session_scope() as session:
            return session.query(ExtendedWorkHours) \
                .filter(
                    ExtendedWorkHours.uid == uid,
                    ExtendedWorkHours.extension_end_time >= start_date,
                    ExtendedWorkHours.extension_end_time <= end_date,
                    ExtendedWorkHours.extension_active == 0
                ).all()
        
    def get_targets(self):
        with self.session_scope() as session:
            return session.query(Target).filter(or_(Target.enabled ==1, Target.enabled==2)).all()

    def get_target_status_by_account_id(self, account_id: int):
        with self.session_scope() as session:
            return session.query(Target, TargetStatus).join(Target, TargetStatus.id_target == Target.id).filter(TargetStatus.std_wrk_id == account_id).all()
'''
Exemplo de Uso da Classe DatabaseManager

Suponha que você queira trabalhar com a tabela Client. Você pode usar a classe DatabaseManager da seguinte forma:

python

from database_manager import DatabaseManager
from models.client import Client

# Configuração do banco de dados PostgreSQL
DATABASE_URL = 'postgresql://username:password@localhost:5432/mydatabase'

# Inicializar o gerenciador do banco de dados
db_manager = DatabaseManager(DATABASE_URL)

# Exemplo: Adicionar um novo cliente
new_client = Client(
    hostname='client2',
    ip_address='192.168.1.2',
    client_version='v1.2',
    os_version='Linux'
)
db_manager.add_entry(new_client)

# Exemplo: Consultar todos os clientes
clients = db_manager.get_all(Client)
for client in clients:
    print(f"ID: {client.get_id()}, Hostname: {client.get_hostname()}")

# Exemplo: Atualizar um cliente pelo ID
update_data = {'hostname': 'client2-updated'}
db_manager.update_entry(Client, id_=1, update_data=update_data)

# Exemplo: Deletar um cliente pelo ID
db_manager.delete_entry(Client, id_=1)
 
'''