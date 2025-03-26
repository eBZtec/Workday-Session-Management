from fastapi import APIRouter

from src.routes.http.v1.auth import  auth_router
from src.routes.http.v1.account import account_router
from src.routes.http.v1.overtime import overtime_router
from src.routes.http.v1.agent import agent_router
from src.routes.http.v1.targets import targets_router


router = APIRouter()

router.include_router(
    auth_router.router,
    prefix="/auth",
    tags=["WSM Authentication"]
)

router.include_router(
    account_router.router,
    prefix="/account",
    tags=["WSM Account"]
)

router.include_router(
    overtime_router.router,
    prefix="/overtime",
    tags=["WSM Overtime"]
)

router.include_router(
    agent_router.router,
    prefix="/agent",
    tags=["WSM Agent"]
)

router.include_router(
    targets_router.router,
    prefix="/target",
    tags=["WSM Target"]
)

