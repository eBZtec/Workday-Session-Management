from fastapi import APIRouter

from src.routes.http.v1.auth import auth_router
from src.routes.http.v1.admin import admin_router 


router = APIRouter()

router.include_router(
    auth_router.router,
    prefix="/auth",
    tags=["WSM Authentication"]
)

router.include_router(
    admin_router.router,
    prefix="/audit",
    tags=["WSM Audit"]
)

