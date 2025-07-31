from pygments.lexer import default
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SessionsAudit(Base):
    __tablename__ = 'session_audit'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String(100),nullable=False)
    event_type = Column(String(50), nullable=False)
    login = Column(String(100), nullable =False)
    status = Column(String(50))
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=True)
    os_version = Column(String(50), nullable=False)
    os_name = Column(String(50))
    ip_address = Column(String(100), nullable=False)
    client_version = Column(String(50), nullable=False)
    agent_info = Column(String(50))


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username= Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
