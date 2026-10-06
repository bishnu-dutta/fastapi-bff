import logging
import uuid
from datetime import UTC, datetime

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.models import Organization, Post, User, UserRole

from .provider import BaseDataProvider

logger = logging.getLogger(__name__)


def _parse_datetime(val: str | None) -> datetime | None:
    """Helper to safely parse an ISO datetime string."""
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val)
        except (ValueError, TypeError) as exc:
            logger.warning("Failed to parse datetime '%s': %s", val, exc)
    return None

class DirectusClient(BaseDataProvider):
    def __init__(self):
        self.base_url = settings.DIRECTUS_BASE_URL.rstrip("/")
        self.token = settings.DIRECTUS_SERVER_TOKEN

    @property
    def headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.request(method, url, headers=self.headers, **kwargs)
                if resp.status_code == 404:
                    return None
                if resp.status_code >= 400:
                    err_detail = resp.text
                    try:
                        err_json = resp.json()
                        if "errors" in err_json and len(err_json["errors"]) > 0:
                            err_detail = err_json["errors"][0].get("message", err_detail)
                    # blind exception, fixed
                    except (ValueError, KeyError, TypeError) as exc: 
                        logger.debug(
                            "Failed to parse directus error JSON response: %s",
                            exc,
                            exc_info=True
                        ) 
                    raise HTTPException(
                        status_code=resp.status_code,
                        detail=f"Directus error: {err_detail}",
                    )
                if resp.status_code == 204:
                    return None
                return resp.json().get("data")
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to communicate with Directus engine: {exc}",
            )

    async def list(self, collection: str, params: dict | None = None):
        res = await self._request("GET", f"/items/{collection}", params=params)
        return res if res is not None else []

    async def get_by_id(self, collection: str, item_id: str | int, params: dict | None = None):
        return await self._request("GET", f"/items/{collection}/{item_id}", params=params)

    async def create(self, collection: str, data: dict, params: dict | None = None):
        return await self._request("POST", f"/items/{collection}", json=data, params=params)

    async def update(self, collection: str, item_id: str, data: dict, params: dict | None = None):
        return await self._request("PATCH", f"/items/{collection}/{item_id}", json=data, params=params)

    async def delete(self, collection: str, item_id: int):
        await self._request("DELETE", f"/items/{collection}/{item_id}")
        return True

def _to_user(data: dict | None) -> User | None:
    """Helper to map Directus JSON response into a User model instance."""
    if not data:
        return None
    # Parse UUID if present
    raw_org = data.get("organization_id")
    org_obj = None
    if isinstance(raw_org, dict):
        raw_uid = raw_org.get("uid") or raw_org.get("id")
        try:
            org_id = uuid.UUID(str(raw_uid)) if raw_uid else None
        # blind exception, fixed
        except (ValueError, KeyError, TypeError) as exc: 
            logger.warning(
                "Invalid organization UUID %r encountered: %s", 
                raw_uid, 
                exc
            )
            org_id = None
        
        org_obj = Organization(
            uid=org_id,
            name=raw_org.get("name")
        )
    elif isinstance(raw_org, str):
        try:
            org_id = uuid.UUID(raw_org)
        # blind exception, fixed
        except (ValueError, KeyError, TypeError) as exc: 
            logger.warning(
                "Invalid organization UUID %r encountered: %s", 
                raw_org, 
                exc
            )
            org_id = None
    else:
        org_id = raw_org
    return User(
        id=data.get("id"),
        username=data.get("username"),
        email=data.get("email"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        keycloak_sub=data.get("keycloak_sub"),
        is_verified=data.get("is_verified") or False,
        provider=data.get("provider", "KeycloakOICD"),
        hashed_password=data.get("hashed_password"),
        role=data.get("role", UserRole.USER),
        organization_id=org_id,
        organization=org_obj,  # <-- Attaches the Organization object!
        is_active=data.get("is_active", True),
        created_at=_parse_datetime(data.get("created_at")) or datetime.now(UTC),
        updated_at=_parse_datetime(data.get("updated_at")),
        trashed_at=_parse_datetime(data.get("trashed_at")),
    )



def _to_post(data: dict | None, owner: User | None = None) -> Post | None:
    if not data:
        return None
    
    raw_user = data.get("user_id")
    if isinstance(raw_user, dict):
        user_id = raw_user.get("id")
        if owner is None:
            owner = _to_user(raw_user)  # <-- Automatically constructs the User owner!
    else:
        user_id = raw_user

    post = Post(
        id=data.get("id"),
        title=data.get("title"),
        content=data.get("content"),
        user_id=user_id,
        is_active=data.get("is_active", True),
        created_at=_parse_datetime(data.get("created_at")) or datetime.now(UTC),
        updated_at=_parse_datetime(data.get("updated_at")),
        trashed_at=_parse_datetime(data.get("trashed_at")),
    )
    if owner:
        post.owner_id = owner
    return post


directus_client = DirectusClient()