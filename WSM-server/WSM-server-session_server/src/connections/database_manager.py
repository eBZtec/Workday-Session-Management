from datetime import datetime, date
from typing import Optional
from sqlalchemy import create_engine, or_, desc, RowMapping
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy import create_engine
from contextlib import contextmanager

from src.enums.target_status_type import TargetStatusType
from src.models.models import Base, TargetStatus, FlexTime
from src.config import config
from src.models.models import Holidays, ExtendedWorkHours, Target, Sessions, Client
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
        
    def get_enable_targets(self):
        with self.session_scope() as session:
            return session.query(Target).filter(Target.enabled==TargetStatusType.ENABLE).all()

    def get_all_targets(self):
        with self.session_scope() as session:
            return session.query(Target).all()

    def get_target_status_by_account_id(self, account_id: int):
        with self.session_scope() as session:
            return session.query(Target, TargetStatus).join(Target, TargetStatus.id_target == Target.id).filter(TargetStatus.std_wrk_id == account_id).all()

    def get_user_session_timezone(self, user_: str):
        with self.session_scope() as session:
            return session.query(Sessions).filter(Sessions.user == user_).all()

    def get_target_by_name(self, name_: Optional [str] = None):
        with self.session_scope() as session:
            query = session.query(Target)
            if name_:
                query = query.filter(Target.target == name_)
            return query.all()
        
        
    def get_all_hosts_sessions(self):
        with self.session_scope() as session:
            return session.query(Sessions).filter(Sessions.status == "active").order_by(Sessions.hostname).all()
            


    def get_host_sessions(self, _host):
        with self.session_scope() as session:
            return session.query(Sessions).filter(Sessions.status == "active", Sessions.hostname == _host).order_by(Sessions.hostname).all()
            


    def get_last_flex_time_by_user_id(self, user_id: int) -> FlexTime | None:
        with self.session_scope() as session:
            return session.query(FlexTime).filter(FlexTime.std_wrk_id==user_id).order_by(desc(FlexTime.id)).first()


    def get_client_info_by_hostname(self, _host):
        with self.session_scope() as session:
            return session.query(Client.hostname,
                                 Sessions.user,
                                 Client.ip_address,
                                 Client.client_version,
                                 Client.os_name,
                                 Client.os_version,
                                 Client.uptime,
                                 Client.agent_info
                                 ).join(Sessions, Sessions.hostname == Client.hostname).filter(Sessions.hostname == _host).all()

    def get_all_sessions_client_info(self):
        with self.session_scope() as session:
            return session.query(Client.hostname,
                                 Sessions.user,
                                 Client.ip_address,
                                 Client.client_version,
                                 Client.os_name,
                                 Client.os_version,
                                 Client.uptime,
                                 Client.agent_info
                                 ).join(Sessions, Sessions.hostname == Client.hostname).all()

    def get_flex_time_by_user_and_date_with_pagination(self, account_id: int, date_from: datetime = None, date_to: datetime = None, skip = 0, limit = 10) -> list[FlexTime]:
        with self.session_scope() as session:
            query = session.query(FlexTime).filter(FlexTime.std_wrk_id == account_id)

            if date_from:
                query = query.filter(FlexTime.work_time >= date_from)
            if date_from:
                query = query.filter(FlexTime.work_time >= date_from)
            return query.offset(skip).limit(limit).all()