from src.config import config
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

# Configurações de segurança
SECRET_KEY = config.OAUTH_SECRET_KEY
ALGORITHM = "HS256"

VALID_SECRET_KEY = config.OAUTH_SECRET_KEY


# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# AuthService class
class AuthService:

    ACCESS_TOKEN_EXPIRE_MINUTES = 30    

    def authenticate_with_secret_key(self, secret_key:str) -> bool:
        # verify the secret key 
        return secret_key == VALID_SECRET_KEY
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    async def get_current_client(self, token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            client_id: str = payload.get("sub")
            if client_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        return client_id