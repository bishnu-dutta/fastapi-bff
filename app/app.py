from app.core.config import settings
from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models
from app.auth.router import router as auth_router

# from app.core.database import async_engine, async_session_dep
from app.core.exceptions import register_exception_handlers
from app.middleware import register_middleware
from app.middleware.logging import setup_logging
from app.organizations.router import router as organizations_router
from app.posts.router import router as posts_router
from app.users.router import router as users_router


setup_logging()


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    # Below are URLs, you can rename the path and it will point to that
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    openapi_url=settings.OPENAPI_URL,
    # Uses our tag created in routers to point to them.
    openapi_tags=[
        {"name": "auth", "description": "Authentication and user token operations with Keycloak."},
        {"name": "users", "description": "User profile management with dual-write to Directus."},
        {"name": "posts", "description": "Post management with dual-write to Directus."},
        {"name": "organizations", "description": "Organization and role management."},
    ],
)

app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(organizations_router)

register_middleware(app)
register_exception_handlers(app)
