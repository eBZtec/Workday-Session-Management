from typing import Union, List
from src.utils.filter_transform import InvalidFilterException, build_sqlalchemy_filter
from sqlalchemy.inspection import inspect
from src.connections.database_manager import DatabaseManager
from src.models.models import SessionsAudit
from src.config.wsm_logger import logger
from typing import Union, List, Any


class ReportController:

    @staticmethod
    async def execute(filter: Union[dict, List[Union[dict, Any]]], page, page_size):
        try:
            session = DatabaseManager()

            #Convert FilterItem (Pydantic) to dict if necessary
            if isinstance(filter, list) and hasattr(filter[0], 'dict'):
                filter = [f.dict() for f in filter]
            filter_expression = build_sqlalchemy_filter(filter, SessionsAudit)
            query = session.search_with_where_clause_paginated(SessionsAudit, filter_expression, page, page_size)
            def to_dict(obj):
                from sqlalchemy.inspection import inspect
                return {column.key: getattr(obj, column.key) for column in inspect(obj).mapper.column_attrs}
            result = [to_dict(obj) for obj in query]
            return result
        except InvalidFilterException as e:
            logger.error(f"Could not search into audit database, because the error: {e}")
