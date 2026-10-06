from fastapi import APIRouter, status

from app.health.response import HealthResponse, PingResponse
from app.health.service import get_health_status

router = APIRouter(tags=["health"])




@router.get(
    "/ping",
    response_model=PingResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness ping",
    description="lightweight liveness probe.",
)
async def ping() -> PingResponse:
    return PingResponse(ping="pong")


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Readiness probe reporting BFF status and upstream Directus and Keycloak connectivity.",
)
async def health() -> HealthResponse:
    return await get_health_status() 
    