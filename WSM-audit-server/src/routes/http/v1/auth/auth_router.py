from fastapi import APIRouter, status

from src.services.auth_service import Token

router = APIRouter()

@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    name="Get authorization token"
)
async def login():
    ...