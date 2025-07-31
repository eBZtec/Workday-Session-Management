from src.models.models import User
from src.connections import database_manager
from src.connections.database import get_db
from src.services.security.security import verify_password
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.config import config
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from src.serialization.token_schema import Token



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/wsm/api/v1/auth/token")

SECRET_KEY = config.OAUTH_SECRET_KEY
ALGORITHM = "HS256"


class AuthService:
    ACCESS_TOKEN_EXPIRE_MINUTES = 30    

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception
        return user
