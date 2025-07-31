from fastapi import  APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from src.services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm
from src.connections.database_manager import DatabaseManager
from src.connections.database import get_db 
from src.serialization.token_schema import Token
router = APIRouter()

auth_service = AuthService()

dm = DatabaseManager()

@router.post(
    "/token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    name="Get JWT Token"
)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    
    access_token = auth_service.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}