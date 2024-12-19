from sqlalchemy import and_, or_, Column
from sqlalchemy.orm import Session
from typing import List, Any, Tuple
from sqlalchemy.sql.expression import BinaryExpression
from datetime import datetime, timedelta

# SQLAlchemy operator mapping
SQLA_OPERATORS = {
    "$eq": lambda col, val: col == val,
    "$ne": lambda col, val: col != val,
    "$lt": lambda col, val: col < val,
    "$lte": lambda col, val: col <= val,
    "$gt": lambda col, val: col > val,
    "$gte": lambda col, val: col >= val,
    "$like": lambda col, val: col.like(val),
    "$in": lambda col, val: col.in_(val),
}

class InvalidFilterException(Exception):
    pass

def build_sqlalchemy_filter(filters: List[dict], model) -> Any:
    """
    Build SQLAlchemy filter expressions dynamically.
    :param filters: List of filter conditions
    :param model: SQLAlchemy model class for table mapping
    :return: SQLAlchemy filter clause
    """
    expressions = []

    for f in filters:
        if "logical" in f:  # Handle nested logical operators
            logical_op = f["logical"].upper()
            nested_conditions = f["conditions"]

            nested_expression = build_sqlalchemy_filter(nested_conditions, model)
            if logical_op == "AND":
                expressions.append(and_(*nested_expression))
            elif logical_op == "OR":
                expressions.append(or_(*nested_expression))
            else:
                raise InvalidFilterException(f"Unsupported logical operator: {logical_op}")
        else:
            field = f.get("field")
            operator = f.get("operator")
            value = f.get("value")

            column = getattr(model, field, None)
            if column is None:
                raise InvalidFilterException(f"Invalid field: {field}")
            
            if isinstance(value, str) and isinstance(column.type.python_type, datetime):
                value = datetime.fromisoformat(value)

                # Ajustar horários para "$lte" e "$gte"
                if operator == "$lte" and value.time() == datetime.min.time():
                    value += timedelta(days=1) - timedelta(seconds=1)
                elif operator == "$gte" and value.time() == datetime.min.time():
                    value = value  # Garante que seja o início do dia

            sql_expr = SQLA_OPERATORS[operator](column, value)
            expressions.append(sql_expr)

    return and_(*expressions)

def paginate_query(query, page: int, page_size: int) -> Tuple:
    """
    Apply pagination to a SQLAlchemy query.
    :param query: SQLAlchemy query object
    :param page: Current page number (1-based)
    :param page_size: Number of items per page
    :return: Tuple containing paginated query and pagination info
    """
    offset = (page - 1) * page_size
    paginated_query = query.limit(page_size).offset(offset)
    return paginated_query, {"page": page, "page_size": page_size}

"""
# Example Usage
if __name__ == "__main__":
    from sqlalchemy import create_engine, Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    # SQLAlchemy setup
    Base = declarative_base()

    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        name = Column(String)
        age = Column(Integer)
        city = Column(String)
        status = Column(String)

    # Database setup (SQLite for demonstration)
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Example filters
    filters = [
        {"field": "age", "operator": "$gte", "value": 30},
        {"field": "city", "operator": "$eq", "value": "New York"},
        {"logical": "OR", "conditions": [
            {"field": "status", "operator": "$eq", "value": "Active"},
            {"field": "status", "operator": "$eq", "value": "Pending"}
        ]}
    ]

    try:
        # Pagination setup
        page = 1  # Page number
        page_size = 10  # Items per page

        # Build the filter
        filter_expression = build_sqlalchemy_filter(filters, User)
        query = session.query(User).filter(filter_expression)

        # Apply pagination
        paginated_query, pagination_info = paginate_query(query, page, page_size)

        # Fetch results
        results = paginated_query.all()
        print("Pagination Info:", pagination_info)
        print("Query Results:", results)
    except InvalidFilterException as e:
        print("Error:", e)
"""