import uuid

from app.models import User
from app.services.directus import _to_user, directus_client


async def find_by_username(username: str) -> User | None:
    users = await directus_client.list(
        "users",
        params={
            "filter[username][_eq]": username,
            "limit": 1,
            "fields": "*,organization_id.*"

        }
        )
    if users:
        return _to_user(users[0])
    return None


async def find_by_email(email:str) -> User | None:
    user_email = await directus_client.list(
        "users",
        params={
            "filter[email][_eq]": email.lower(),
            "limit": 1,
            "fields": "*,organization_id.*"
        }
        )
    if user_email:
        return _to_user(user_email[0])
    return None


async def find_by_userid(id:int) -> User | None:
    user_id = await directus_client.get_by_id(
        "users",
        id,
        params={"fields": "*,organization_id.*"}
    )
    if user_id:
        return _to_user(user_id)
    return None
    

async def find_by_keycloak_sub(keycloak_sub:uuid.UUID) -> User | None:
    user_keycloak_sub = await directus_client.list(
        "users",
        params={
            "filter[keycloak_sub][_eq]": keycloak_sub,
            "limit": 1,
            "fields": "*,organization_id.*"
        }
        )
    if user_keycloak_sub:
        return _to_user(user_keycloak_sub[0])
    return None