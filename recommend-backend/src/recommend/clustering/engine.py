from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.recommend.clustering.config import settings

PG_HOST = settings.postgres_host
PG_PORT = settings.postgres_port
PG_USER = settings.postgres_user
PG_PASSWORD = settings.postgres_password
PG_DB = settings.postgres_db

ASYNC_DATABASE_URL = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)