from typing import Union, List
from src.utils.filter_transform import InvalidFilterException, build_sqlalchemy_filter
from sqlalchemy.inspection import inspect
from src.connections.database_manager import DatabaseManager
from src.models.models import SessionsAudit
from src.config.wsm_logger import logger


class ReportController:

    @staticmethod
    async def execute(filter: Union[dict, List[dict]], page, page_size):
        try:
            session = DatabaseManager()
            filter_expression = build_sqlalchemy_filter(filter, SessionsAudit)
            query = session.search_with_where_clause_paginated(SessionsAudit, filter_expression,page,page_size)
            #print("Full Query with Parameters:", query.statement.compile(compile_kwargs={"literal_binds": True}))
            #print("Generated Query:", str(query))   
            def to_dict(obj):
                return {column.key: getattr(obj, column.key) for column in inspect(obj).mapper.column_attrs}
                  
            result = [to_dict(obj) for obj in query]

            return result
        except InvalidFilterException as e:
            logger.error(f"Could not search into audit database, because the error: {e} ")
            print("Error:", e)
        