from pygments.lexer import default
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text, PrimaryKeyConstraint, event, Date
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

from src.enums.types import JourneyType
from src.models.schema.request_models import SessionTerminationActionSchema
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Função para adicionar o evento de atualização de timestamp
def add_update_timestamp_listener(cls):
    @event.listens_for(cls, 'before_update')
    def receive_before_update(mapper, connection, target):
        target.update_timestamp = datetime.now(datetime.timezone.utc)

# Classe base para modelos com update_timestamp
class TimestampedBase(Base):
    __abstract__ = True
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=True)

class Certificate_Authority(Base):
    __tablename__ = 'certificate_authority'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fqdn = Column(String(100), nullable=False)
    certificate = Column(Text, nullable=False)
    validity = Column(DateTime(timezone=True), nullable=False)

    # Relacionamento com Client
    client = relationship("Client", back_populates="certificate_authority", uselist=False, cascade="all, delete-orphan")


# Classe Client
class Client(TimestampedBase):
    __tablename__ = 'client'
    hostname = Column(String(100),primary_key=True, nullable=False)
    ip_address = Column(String(100), nullable=False)
    client_version = Column(String(50), nullable=False)
    os_name = Column(String(50))
    os_version = Column(String(50), nullable=False)
    uptime = Column(Integer, nullable=True)
    agent_info = Column(String(50))
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=True)

    # Relationship with Sessions
    sessions = relationship("Sessions", back_populates="client", cascade='all, delete')


    # Foreign Key to Certificate_Authority
    certificate_authority_id = Column(Integer, ForeignKey('certificate_authority.id'), unique=True, nullable=True)

    # Relationship with Certificate_Authority
    certificate_authority = relationship("Certificate_Authority", back_populates="client", uselist=False)



class Sessions(TimestampedBase):
    __tablename__ = 'sessions'
    hostname = Column(String(100), ForeignKey('client.hostname'),nullable=False)
    event_type = Column(String(50), nullable=False)
    user = Column(String(100), nullable =False)
    status = Column(String(50))
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=True)
    
    __table_args__ = (
    PrimaryKeyConstraint('user', 'hostname'),
    )

    client = relationship("Client", back_populates="sessions")

    # events = relationship("Events", back_populates="session", cascade='all, delete')

class Events(TimestampedBase):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # session_id = Column(Integer, ForeignKey('sessions.id'))
    event_type = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=True)

    # Relacionamento com Sessions
    # session = relationship("Sessions", back_populates="events", cascade='all, delete')

class StandardWorkHours(TimestampedBase):
    __tablename__ = 'standard_workhours'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(50), nullable=False, unique=True)
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)
    allowed_work_hours = Column(Text, nullable=True)
    uf = Column(String(2), nullable=False)
    st = Column(String(35), nullable=False)
    c = Column(String(100), nullable=False)
    weekdays = Column(String(7), nullable=False)
    journey = Column(String(15), nullable=False, default=JourneyType.FLEX_TIME)
    session_termination_action = Column(String(15), default=SessionTerminationActionSchema.LOGOFF)
    cn = Column(String(240), nullable=False)
    l = Column(String(240))
    unrestricted = Column(Boolean, default=False)
    enable = Column(Boolean, nullable=False, default=True)
    deactivation_date = Column(DateTime(timezone=True),nullable=True)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamento com Messages
    messages_entries = relationship("Messages", back_populates="standard_workhours", cascade='all, delete')

    # Relacionamento com TargetStatus
    target_status_entries = relationship("TargetStatus", back_populates="standard_workhours", cascade='all, delete')

     # Relacionamento com ExtendedWorkhours
    extended_workhours_entries = relationship("ExtendedWorkHours", back_populates="standard_workhours", cascade='all, delete')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class FlexTime(TimestampedBase):
    __tablename__ = 'flex_time'
    id = Column(Integer, primary_key=True, autoincrement=True)
    std_wrk_id = Column(Integer, ForeignKey('standard_workhours.id'), nullable=True) # antigo num_reg
    work_time = Column(DateTime(timezone=True), nullable=False)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamento com StandardWorkHours
    standard_workhours = relationship("StandardWorkHours",cascade='all, delete')


# Classe Messages (tabela messages)
class Messages(TimestampedBase):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    std_wrk_id = Column(Integer, ForeignKey('standard_workhours.id'), nullable=True) # antigo num_reg
    uid = Column(String(50), nullable=False)
    message = Column(String(200), nullable=False)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamento com StandardWorkHours
    standard_workhours = relationship("StandardWorkHours", back_populates="messages_entries",cascade='all, delete')


class Exceptions(TimestampedBase):
    __tablename__ = 'exceptions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50))
    ip_address = Column(String(50))
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

class ExtendedWorkHours(TimestampedBase):
    __tablename__ = 'extended_workhours'
    id = Column(Integer, primary_key=True, autoincrement=True)
    std_wrk_id = Column(Integer, ForeignKey('standard_workhours.id'), nullable=False)
    uid = Column(String)  ## usado pra procurar o stdwrkhours
    extension_start_time = Column(DateTime(timezone=False), nullable=False)
    extension_end_time = Column(DateTime(timezone=False), nullable=False)
    extended_workhours_type = Column(String(2), nullable=False)
    uf = Column(String(2), nullable=False)
    c = Column(String(100), nullable=False)
    week_days_count = Column(String(7), nullable=False)
    extension_active = Column(Integer, nullable=False)
    ou = Column(Integer)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamento com StandardWorkHours
    standard_workhours = relationship("StandardWorkHours", back_populates="extended_workhours_entries",cascade="all,delete")

# Classe de Feriados
class Holidays(TimestampedBase):
    __tablename__ = 'holidays'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    day = Column(Integer, primary_key=True, nullable=False)
    month = Column(Integer, primary_key=True, nullable=False)
    city = Column(Integer, nullable=False)
    holiday_type = Column(String(2), nullable=False)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)


class TargetStatus(TimestampedBase):
    __tablename__ = 'target_status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    std_wrk_id = Column(Integer, ForeignKey('standard_workhours.id'), nullable=True)
    id_target = Column(Integer, ForeignKey('target.id'), nullable=False)
    uuid = Column(String(37))
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamento com StandardWorkHours
    standard_workhours = relationship("StandardWorkHours", back_populates="target_status_entries", cascade='all, delete')

    # Relacionamento com Target
    target = relationship("Target", back_populates="target_status_entries", cascade='all, delete')

class Target(TimestampedBase):
    __tablename__ = 'target'
    id = Column(Integer, primary_key=True, autoincrement=True)
    target = Column(String(100), nullable=False)
    service = Column(String(100), nullable=False)
    enabled = Column(Integer, nullable=False)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamento com TargetStatus
    target_status_entries = relationship("TargetStatus", back_populates="target", cascade='all, delete')



