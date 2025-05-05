from sqlalchemy import create_engine, or_, select
from sqlalchemy.orm import sessionmaker
from src.models.models import StandardWorkHours, ExtendedWorkHours, Sessions, Certificate_Authority, Configuration
from dotenv import load_dotenv
from sqlalchemy import create_engine
from contextlib import contextmanager
from src.models.models import Base
from src.config import config
import os, json

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

    def get_id_by_uid(self, model,uid_):
        with self.session_scope() as session:
            return session.query(model.id).filter_by(uid=uid_).scalar()


    def get_by_uid(self, model, uid_):
        with self.session_scope() as session:
            return session.query(model).filter_by(uid=uid_).first()
        
    def get_by_employee_id(self,model,employee_id_):
        with self.session_scope() as session:
            return session.query(model).filter_by(employee_id=employee_id_).first()

    def get_id_by_hostname(self,model,hostname):
        with self.session_scope() as session:
            return session.query(model.id).filter_by(hostname=hostname).first()
        
    def get_by_hostname(self,model,hostname):
        with self.session_scope() as session:
            return session.query(model).filter_by(hostname=hostname).first()

    def get_by_hostname_and_user(self, model, hostname, user):
        with self.session_scope() as session:
            return session.query(model).filter(model.hostname == hostname,model.user == user).first()

    def get_session_by_client_id(self,model,client_id):
        with self.session_scope() as session:
            return session.query(model).filter_by(client_id=client_id).first()

    def get_event_by_event_type(self,model,event_type):
        with self.session_scope() as session:
            return session.query(model).filter_by(event_type=event_type).first()
            
    def update_by_hostname_and_user(self, model, hostname, user, update_data):
        with self.session_scope() as session:
            entry = session.query(model).filter(model.hostname == hostname,model.user == user).first()
            if entry:
                for key, value in update_data.items():
                    setattr(entry,key,value)
                session.commit()
                return entry
            return None

    def delete_user_disconnected(self,model,_hostname,_user):
        with self.session_scope() as session:
            entry = session.query(model).filter(model.hostname == _hostname, model.user ==_user).first()
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False

    def get_cert_by_fqdn(self,model,fqdn_):
        with self.session_scope() as session:
            return session.query(model).filter_by(fqdn=fqdn_).first()


    """
    PONTUAL QUERIES

    """
    #return to client the workhours with extensions
    def get_user_work_time(self,_user):
        with self.session_scope() as session:
            query = (
                select(
                    StandardWorkHours.id.label("std_id"),
                    StandardWorkHours.start_time.label("std_start_time"),
                    StandardWorkHours.end_time.label("std_end_time"),
                    ExtendedWorkHours.extension_start_time.label("ext_start_time"),
                    ExtendedWorkHours.extension_end_time.label("ext_end_time"),
                    StandardWorkHours.weekdays.label("std_weekdays"),
                    ExtendedWorkHours.week_days_count.label("ext_weekdays"),
                )
                .outerjoin(
                    ExtendedWorkHours,
                    StandardWorkHours.uid == ExtendedWorkHours.uid
                )
                .where(StandardWorkHours.uid == _user)
            )
    # Executa a consulta
        results = session.execute(query).fetchall()
        
        return results

    #Get user workdays
    def get_weekdays_work_time(self, _user):
        with self.session_scope() as session:
            # Query para buscar os dias da semana (weekdays)
            query = (
                select(StandardWorkHours.weekdays)
                .where(StandardWorkHours.uid == _user)
            )
            result = session.execute(query).scalar_one_or_none()

            if result:
                # Mapeando os valores para dias da semana
                days_map = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                work_days = [day for idx, day in enumerate(days_map) if result[idx] == "1"]
                return work_days
            else:
                return None


    def get_hostname_by_uid(self, _uid):
        with self.session_scope() as session:
            result = session.query(Sessions.hostname).filter(Sessions.user == _uid).first()
            return result[0] if result else None

    def get_sessions_by_uid(self,_uid):
        with self.session_scope() as session:
            return session.query(Sessions).filter(Sessions.user == _uid).all()

    def get_cert_by_hostname(self,_hostname):
        with self.session_scope() as session:
            return session.query(Certificate_Authority.certificate).filter(Certificate_Authority.fqdn == _hostname).first()

    def get_user_schedule(self,_uid):
        with self.session_scope() as session:
            # Retrieve default user work time
            std_workhours = session.query(StandardWorkHours).filter(StandardWorkHours.uid == _uid).first()
            if std_workhours:
                #Retrieve work time extensions
                extended_workhours = session.query(ExtendedWorkHours).filter(ExtendedWorkHours.uid == _uid, ExtendedWorkHours.extension_active == 1).all()
                # convert allowed time to dict
                allowed_schedule = {day.lower(): [] for day in ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]}
                if std_workhours.allowed_work_hours:
                    standard_hours = json.loads(std_workhours.allowed_work_hours)
                    for day, periods in standard_hours.items():
                        allowed_schedule[day.lower()].extend(periods)

                # Adiciona as extensões de horário
                for ext in extended_workhours:
                    ext_start_minutes = ext.extension_start_time.hour * 60 + ext.extension_start_time.minute
                    ext_end_minutes = ext.extension_end_time.hour * 60 + ext.extension_end_time.minute
                    weekday = ext.extension_start_time.strftime("%A").lower()
                    allowed_schedule[weekday].append({"start": ext_start_minutes, "end": ext_end_minutes})

                # Retorna o JSON
                return allowed_schedule
            else:
                return None
            
    def get_grace_login(self):
        with self.session_scope() as session:
            result = session.query(Configuration.grace_login).filter(Configuration.id == 1).first()
            return result[0] if result else None


