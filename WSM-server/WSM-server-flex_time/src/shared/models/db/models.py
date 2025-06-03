from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from src.shared.enums.types import JourneyType
from src.shared.models.schemas.request_models import SessionTerminationActionSchema

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


class StandardWorkHours(TimestampedBase):
    __tablename__ = 'standard_workhours'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(50), nullable=False, unique=True)
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)
    allowed_work_hours = Column(Text, nullable=True)
    logon_hours = Column(Text, nullable=True)
    formatted_work_hours = Column(Text, nullable=True)
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
    lock = Column(Boolean, default=False)
    disable_reason = Column(String(240))
    active_directory_account_status = Column(Boolean, nullable=True)
    block_station_during_interval = Column(Boolean, default=False)
    block_station_during_interval_in_minutes = Column(Integer, nullable=True)
    deactivation_date = Column(DateTime(timezone=True),nullable=True)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

     # Relacionamento com ExtendedWorkhours
    extended_workhours_entries = relationship("ExtendedWorkHours", back_populates="standard_workhours", cascade='all, delete')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class FlexTime(TimestampedBase):
    __tablename__ = 'flex_time'
    id = Column(Integer, primary_key=True, autoincrement=True)
    std_wrk_id = Column(Integer, ForeignKey('standard_workhours.id'), nullable=True)
    work_time_type = Column(String(10), nullable=False)
    work_time = Column(DateTime(timezone=True), nullable=False)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamento com StandardWorkHours
    standard_workhours = relationship("StandardWorkHours",cascade='all, delete')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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




