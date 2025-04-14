from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session


class WSMRepository(ABC):
    def get_by_id(self, _id: int, session: Session, model: Any):
        return session.query(model).get(_id)

    def get_by_filter(self, session: Session, model: Any, filters: dict):
        return session.query(model).filter_by(**filters).all()

    def get_last_record(self, session: Session, model: Any, filters: dict):
        return session.query(model).filter_by(**filters).order_by(desc(model.id)).first()