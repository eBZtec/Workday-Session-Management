from typing import Generator
from sqlalchemy.orm import Session
from src.connections.database_manager import DatabaseManager

db_manager = DatabaseManager()

def get_db() -> Generator[Session,None,None]:
    """
    Função para uso com Depends(get_db) no FastAPI.
    Ela delega para o session_scope do DatabaseManager.
    """
    with db_manager.session_scope() as session:
        yield session  # type: ignore
