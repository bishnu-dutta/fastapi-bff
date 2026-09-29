from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import (
    http_exception_handler,
)
from starlette.exceptions import HTTPException as StarletteHTTPException


async def custom_http_exception_handler(
    request: Request, exc: HTTPException | StarletteHTTPException
):
    request.state.error_detail = exc.detail
    return await http_exception_handler(request, exc)


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(HTTPException, custom_http_exception_handler)