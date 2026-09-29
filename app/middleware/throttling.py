import time
from collections import defaultdict

from fastapi import FastAPI, Request, status
from starlette.responses import JSONResponse

rate_limit = 5       
time_window = 60      
endpoint = "/auth/token" 

history = defaultdict(list)


def ThrottlingMiddleware(app:FastAPI):
    @app.middleware("http")
    async def custom_throttling(request:Request, call_next):
        if request.url.path == endpoint:
            client_ip = request.client.host if request.client else "unknown"
            current_time = time.time()

            dict_list = []
            for t in history[client_ip]:
                if current_time - t < time_window:
                    dict_list.append(t)
            
            history[client_ip] = dict_list

            if len(history[client_ip]) >= rate_limit:
                retry_after = int(time_window - (current_time - history[client_ip][0]))
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Too Many Requests",
                        "detail": f"Too many login attempts. Please try again in {retry_after} seconds."
                    },
                )

            history[client_ip].append(current_time)

        return await call_next(request)