import logging
import time
from http import HTTPStatus

from fastapi import FastAPI, Request

logger = logging.getLogger("uvicorn.access")
logger.disabled = True



def LoggingMiddleware(app:FastAPI):
    @app.middleware("http")
    async def custom_logging (request: Request, call_next):   

        start_time = time.perf_counter()


        client_ip = request.client.host if request.client else "unknown"
        client_port = request.client.port if request.client else "unknown"

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        detail = getattr(request.state, "error_detail", None)

        message = f"Method: {request.method}\nURL: {request.url}\n" \
                  f"IP: {client_ip}\nPORT: {client_port}\n" \
                  f"STATUS: {response.status_code} {HTTPStatus(response.status_code).phrase}\n" \
                  f"Message: {detail if detail else 'Successfully completed operation for endpoint'}\n" \
                  f"Time taken: {process_time} seconds\n"

        print(message)
        return response



        