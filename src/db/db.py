from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

engine = create_async_engine(settings.db_config.get_db_url("async"), pool_pre_ping=True)
async_session_factory = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession, autoflush=False
)


class Base(DeclarativeBase):
    pass


def run_migrations() -> None:
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.db_config.get_db_url("sync"))
    command.upgrade(alembic_cfg, "head")
