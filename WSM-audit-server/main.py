from contextlib import asynccontextmanager
from src.connections.scheduler import scheduler
import uvicorn
from fastapi import FastAPI, Depends, Form
from src.routes.http.router import api_router
from src.config.wsm_logger import logger


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
   uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
   logger.info("Running Audit Server ...")


