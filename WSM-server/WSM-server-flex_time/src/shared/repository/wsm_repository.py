from abc import ABC
from typing import Any
from datetime import datetime

from sqlalchemy import desc, select, and_
from sqlalchemy.orm import Session

from src.shared.models.db.models import FlexTime


class WSMRepository(ABC):
    def get_by_id(self, _id: int, session: Session, model: Any):
        return session.query(model).get(_id)

    def get_by_filter(self, session: Session, model: Any, filters: dict):
        return session.query(model).filter_by(**filters).all()

    def get_last_record(self, session: Session, model: Any, filters: dict):
        return session.query(model).filter_by(**filters).order_by(desc(model.id)).first()

    def get_flex_times_between_datetime(self, session: Session, _id: int, start: datetime, end: datetime):
        stmt = select(FlexTime).where(
            and_(
                FlexTime.work_time.between(start, end),
                FlexTime.std_wrk_id == _id
            )
        ).order_by(FlexTime.create_timestamp)

        return session.execute(stmt).scalars().all()