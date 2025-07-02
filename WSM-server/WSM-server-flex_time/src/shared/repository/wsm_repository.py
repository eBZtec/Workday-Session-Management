from abc import ABC
from typing import Any
from datetime import datetime, date, UTC, timezone

from sqlalchemy import desc, select, and_, Sequence
from sqlalchemy.orm import Session

from src.shared.models.db.models import FlexTime, ExtendedWorkHours


class WSMRepository(ABC):
    def get_by_id(self, _id: int, session: Session, model: Any):
        return session.query(model).get(_id)

    def get_by_filter(self, session: Session, model: Any, filters: dict):
        return session.query(model).filter_by(**filters).all()

    def get_last_record(self, session: Session, model: Any, filters: dict):
        return session.query(model).filter_by(**filters).order_by(desc(model.id)).first()

    def get_flex_times_between_datetime(self, session: Session, _id: int, start: datetime, end: datetime) -> Sequence[FlexTime]:
        stmt = select(FlexTime).where(
            and_(
                FlexTime.work_time.between(start, end),
                FlexTime.std_wrk_id == _id
            )
        ).order_by(FlexTime.create_timestamp)

        return session.execute(stmt).scalars().all()

    def get_active_extensions_for_today(self, _id: int, session: Session) -> list[tuple[datetime, datetime]]:
        extensions = []
        start_date = datetime.now(UTC)
        end_date = date.fromordinal(start_date.toordinal() + 6)
        end_date = datetime(
            end_date.year,
            end_date.month,
            end_date.day,
            23,
            59,
            0,
            tzinfo=UTC
        )
        results = session.query(ExtendedWorkHours).filter(
            ExtendedWorkHours.std_wrk_id == _id,
            ExtendedWorkHours.extension_end_time >= start_date,
            ExtendedWorkHours.extension_end_time <= end_date,
            ExtendedWorkHours.extension_active == 0
        ).all()

        for row in results:
            extension = (WSMRepository.to_utc(row.extension_start_time), WSMRepository.to_utc(row.extension_end_time))
            extensions.append(extension)

        return extensions

    @staticmethod
    def to_utc(data: datetime):
        return data.replace(tzinfo=timezone.utc)