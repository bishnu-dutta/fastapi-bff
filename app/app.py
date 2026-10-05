from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models
from app.auth.router import router as auth_router

from app.middleware.logging import setup_logging

# from app.core.database import async_engine, async_session_dep
from app.core.exceptions import register_exception_handlers
from app.middleware import register_middleware
from app.organizations.router import router as organizations_router
from app.posts.router import router as posts_router
from app.users.router import router as users_router





@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # await async_engine.dispose()


setup_logging()
app = FastAPI()
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(organizations_router)

register_middleware(app)
register_exception_handlers(app)
