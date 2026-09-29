from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

from .context import session_context

'''
we can also do 
async_engine = create_async_engine(settings.database_url, echo=False)
'''


# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")
# if not DATABASE_URL:
#     raise RuntimeError("DATABASE_URL environment variable is not set in .env")


# creating async engine
async_engine = create_async_engine(settings.database_url, echo=False)

# creating session factory
async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

# now with alembic, it handles table create Base.metadata.create_all()


# creating a local session for each request
async def async_session_local() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        token = session_context.set(session)
        try:
            yield session
        finally:
            session_context.reset(token)
            await session.close()

# dependency variable to be imported 
async_session_dep = Depends(async_session_local)