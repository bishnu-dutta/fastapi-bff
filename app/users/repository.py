
import uuid

from pydantic import EmailStr

from app.core.context import get_current_org_id
from app.models import User, UserRole, Organization
from app.organizations.request import AdminCreateUserRequest
from .request import CreateUserRequest, UpdateUserRequest

from app.services.directus import directus_client, _to_user


async def save_user_to_database(data: CreateUserRequest | AdminCreateUserRequest, keycloak_sub:uuid.UUID ,role: UserRole, organization_id: uuid.UUID) -> User:
    payload = {
        "username":data.username,
        "email":data.email.lower(),
        "is_verified":False,
        "organization_id":str(organization_id),
        "role":role.value if hasattr(role, "value") else str(role),
        "keycloak_sub": keycloak_sub,
        "first_name": data.first_name,
        "last_name": data.last_name
    }

    user = await directus_client.create(
        "users", 
        payload,  
        params={"fields": "*,organization_id.*"}
    )
    return _to_user(user)

    
# async def update_user_otp(user: User,otp_hash: str,otp_expiry: datetime) -> User:
#     payload = {
#         "otp_hash": otp_hash,
#         "otp_expiry": otp_expiry.isoformat() if otp_expiry else None,
#         "otp_attempts": 0,
#     }
#     updated = await directus_client.update("users", str(user.id), payload)
#     return _to_user(updated)


async def find_user_by_email(email:EmailStr) -> User | None:
    existing_mail = await directus_client.list(
        "users"
        , params={
            "filter[email][_eq]": email.lower(), 
            "limit": 1}
        )
    if existing_mail:
        return _to_user(existing_mail[0])
    return None


async def find_user_by_username(username: str) -> User | None:
    existing_user = await directus_client.list(
        "users",
        params={
            "filter[username][_eq]": username,
            "limit": 1
        }
    )
    if existing_user:
        return _to_user(existing_user[0])
    return None


async def find_user_by_email_and_username(email:EmailStr, username: str) -> User | None:
    existing= await directus_client.list(
        "users"
        , params={
            "filter[_or][0][email][_eq]": email.lower(), 
            "filter[_or][1][username][_eq]": username.lower(),
            "limit": 1}
        )
    if existing:
        return _to_user(existing[0])
    return None



async def all_users(offset:int,limit:int) -> list[User]:
    org_id = get_current_org_id()
    params = {
        "limit": limit,
        "offset": offset,
        "sort": "id",
        "fields": "*,organization_id.*",
    }
    if org_id:
        params["filter[organization_id][_eq]"] = str(org_id)
    all_users = await directus_client.list("users", params=params)
    return [_to_user(item) for item in all_users] if all_users else []

 
async def find_user_by_id(id: int) -> User | None:
    org_id = get_current_org_id()
    user_data = await directus_client.get_by_id(
        "users",
        id,
        params= {"fields": "*,organization_id.*"},
        )
    if not user_data:
        return None

    user = _to_user(user_data)
    if not user:
        return None

    if org_id and str(user.organization_id) != str(org_id):
        return None
    return user


async def delete_user_by_id(id: int) -> User | None:
    user = await find_user_by_id(id)
    if user:
        await directus_client.delete(
            "users",
            id
            )
    return user


async def update_user_by_id(id: int, data: UpdateUserRequest) -> User | None:
    user = await find_user_by_id(id)
    if not user:
        return None
    payload = {}
    if data.username is not None:
        payload["username"] = data.username
    if data.email is not None:
        payload["email"] = data.email.lower()
    if data.first_name is not None:
        payload["first_name"] = data.first_name
    if data.last_name is not None:
        payload["last_name"] = data.last_name
    if payload:
        updated = await directus_client.update(
            "users", 
            str(id), 
            payload,  
            params={"fields": "*,organization_id.*"}
        )
        return _to_user(updated)
    return user

# async def update_password_by_email(user: User, password: str) -> User | None:
#     payload = {
#         "hashed_password": hash_password(password)
#     }
#     updated = await directus_client.update("users", str(user.id), payload)
#     return _to_user(updated)

    
# async def mark_user_verified(user_id: int) -> User | None:
#     payload = {
#         "is_verified": True,
#         "otp_hash": None,
#         "otp_expiry": None,
#         "otp_attempts": 0,
#     }
#     updated = await directus_client.update("users", str(user_id), payload)
#     return _to_user(updated)  


# async def increment_otp_attempts(user_id: int, attempts: int) -> User | None:
#     payload = {"otp_attempts": attempts}
#     updated = await directus_client.update("users", str(user_id), payload)
#     return _to_user(updated)