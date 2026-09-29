from fastapi import FastAPI

from .logging import LoggingMiddleware
from .throttling import ThrottlingMiddleware


def register_middleware(app:FastAPI):
    ThrottlingMiddleware(app)
    LoggingMiddleware(app)