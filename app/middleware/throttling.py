import time
from collections import defaultdict

from fastapi import FastAPI, Request, status
from starlette.responses import JSONResponse

endpoint_rules = {
    # auth routes
    "/auth/token": {
        "rate_limit": 5,
        "time_window": 60,
    },
    # users route
    "/users/create": {
        "rate_limit": 5,
        "time_window": 60,
    },
    "/users/forgot-password": {
        "rate_limit": 1,
        "time_window": 60,
    },
    "/users/resend-verification-mail": {
        "rate_limit": 1,
        "time_window": 60,
    },
    # posts routes
    "/user/post/create": {
        "rate_limit": 5,
        "time_window": 60,
    }
}

history = defaultdict(list)


def ThrottlingMiddleware(app:FastAPI):
    @app.middleware("http")
    async def custom_throttling(request:Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)
        path = request.url.path.rstrip("/") or "/"
        if path in endpoint_rules:
            rate_limit = endpoint_rules[path]["rate_limit"]
            time_window = endpoint_rules[path]["time_window"]

            client_ip = request.client.host if request.client else "unknown"
            key = (client_ip, path)
            current_time = time.time()

            history[key] = [
                t for t in history[key] if current_time - t < time_window
            ]

            if len(history[key]) >= rate_limit:
                retry_after = max(1, int(time_window - (current_time - history[key][0])))
                error_detail = f"Too many {path} attempts. Please try again in {retry_after} seconds."

                request.state.error_detail = error_detail

                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    headers={"Retry-After": str(retry_after)},
                    content={
                        "error": "Too Many Requests",
                        "detail": error_detail
                    },
                )

            history[key].append(current_time)

        return await call_next(request)