from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers import router
from src.db.db import run_migrations
from src.middleware.exception_handler import ExceptionHandlingMiddleware
from src.utils.schedule_task import check_status

from apscheduler.schedulers.asyncio import AsyncIOScheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_status, "interval", seconds=5)
    scheduler.start()

    try:
        yield
    finally:
        scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.add_middleware(ExceptionHandlingMiddleware)
