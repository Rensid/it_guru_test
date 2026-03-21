from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers import router
from src.db.db import run_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)
