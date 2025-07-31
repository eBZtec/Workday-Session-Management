from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.config.wsm_logger import logger
from src.connections.scheduler import scheduler
from src.routes.http.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    logger.info("AsyncIO Scheduler started")

    yield

    scheduler.shutdown()
    logger.info("AsyncIO Scheduler shutdown")


app = FastAPI(lifespan=lifespan)
# fastapi dev main.py

# Instance of the authentication service

app.include_router(
    api_router,
    prefix="/wsm/api"
)


def main():
    pass

if __name__ == "__main__":
   main()


