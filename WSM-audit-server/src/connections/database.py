from typing import Generator
from sqlalchemy.orm import Session
from src.connections.session_database_manager import SessionDatabaseManager

db_manager = SessionDatabaseManager()

def get_db() -> Generator[Session,None,None]:
    """
    Função para uso com Depends(get_db) no FastAPI.
    Ela delega para o session_scope do DatabaseManager.
    """
    with db_manager.session_scope() as session:
        yield session  # type: ignore
