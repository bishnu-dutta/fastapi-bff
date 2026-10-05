import logging
import time
from http import HTTPStatus

from fastapi import FastAPI, Request

access_logger = logging.getLogger("app.access")

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        # overwriting any default Uvicorn handler
        force=True,  
    )

    logging.getLogger("app").setLevel(logging.DEBUG)
    # Silence third-party noise by setting logging level to WARNING for httpx calls to Directus & Keycloak
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").disabled = True



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

        if response.status_code >= 500:
            access_logger.error(message)
        elif response.status_code >= 400:
            access_logger.warning(message)
        else:
            access_logger.info(message)
        
        return response



        