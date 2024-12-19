from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Form
from src.routes.http.router import api_router
from src.services.auth_service import AuthService, Token

app = FastAPI()
# fastapi dev main.py

# Instance of the authentication service

app.include_router(
    api_router,
    prefix="/wsm/api"
)

auth_service = AuthService()

# Login route to get token
@app.post("/token", response_model=Token)
async def login_for_access_token(secret_key: str = Form(...)):
    # Valida a chave secreta
    if not auth_service.authenticate_with_secret_key(secret_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid secret key"
        )
    # Generate token JWT
    access_token = auth_service.create_access_token(
        data={"sub": "client"},  # O "sub" pode ser qualquer identificação do cliente
        expires_delta=timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


def main():
    pass

if __name__ == "__main__":
   main()


