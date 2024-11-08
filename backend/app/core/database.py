from venv import create

from requests import session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import Session

from .config import settings

# Sync engine
engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,
    echo=settings.DEBUG
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

# Dependency for sync operations
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for async operations
async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
