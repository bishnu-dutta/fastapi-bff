import asyncio
import logging

import httpx

from app.core.config import settings
from app.health.response import HealthResponse

logger = logging.getLogger(__name__)


async def _check_directus(client: httpx.AsyncClient) -> str:
    try:
        url = f"{settings.DIRECTUS_BASE_URL.rstrip('/')}/server/ping"
        resp = await client.get(url)
        if resp.status_code == 200:
            return "connected"
        # if anything else than 200 return unavailable
        logger.warning(
            "Directus health probe returned non-200 status code %s: %s",
            resp.status_code,
            resp.text,
        )
        return "unavailable"
    # logging the exception
    except httpx.RequestError:
        logger.exception("Directus health probe failed")
        return "unavailable"
        



async def _check_keycloak(client: httpx.AsyncClient) -> str:
    try:
        url = f"{settings.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{settings.KEYCLOAK_REALM}"
        resp = await client.get(url)
        if resp.status_code == 200:
            return "connected"
        # if anything else than 200 return unavailable
        logger.warning(
            "Keycloak health probe returned non-200 status code %s: %s",
            resp.status_code,
            resp.text,
        )
        return "unavailable"
    # logging the exception 
    except httpx.RequestError:
        logger.exception("Keycloak health probe failed")
        return "unavailable"

async def get_health_status() -> HealthResponse:
    async with httpx.AsyncClient(timeout=3.0) as client:
        directus_status, keycloak_status = await asyncio.gather(
            _check_directus(client),
            _check_keycloak(client),
        )
    if directus_status == "connected" and keycloak_status == "connected":
        overall_status = "healthy"
    elif directus_status == "connected" or keycloak_status == "connected":
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"
    return HealthResponse(
        status=overall_status,
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        directus=directus_status,
        keycloak=keycloak_status,
    )