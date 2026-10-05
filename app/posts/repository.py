from datetime import UTC, datetime

from app.core.context import get_current_org_id
from app.models import Post, User
from app.services.directus import _to_post, directus_client
from app.users.repository import find_user_by_id

from .request import CreatePostRequest, UpdatePostRequest


async def save_post_to_database(data: CreatePostRequest, current_user_id: int, current_user: User):
    payload = {
        "user_id":current_user_id,
        "title":data.title,
        "content":data.content,
        "created_at": datetime.now(UTC).isoformat(),
        "is_active":True,
        "trashed_at": None
    }
    post = await directus_client.create("posts", payload)
    return _to_post(post, owner=current_user)

async def get_all_posts_from_database(offset:int,limit:int) -> list[Post]:
    org_id = get_current_org_id()
    params = {
        "limit": limit,
        "offset": offset,
        "sort": "id",
        "fields":"*,user_id.*",
        # where trash_at is NULL and is_active is True
        "filter[is_active][_eq]":True,
        "filter[trashed_at][_null]":True
    }
    if org_id:
        params["filter[user_id][organization_id][_eq]"] = str(org_id)
    all_posts = await directus_client.list("posts", params=params)
    return [_to_post(post) for post in all_posts] if all_posts else []


async def get_all_post_by_user_id_from_database(user_id: int, offset: int, limit: int) -> list[Post]:
    org_id = get_current_org_id()
    user = await find_user_by_id(user_id)
    if not user:
        return []
    if org_id and str(user.organization_id) != str(org_id):
        return []
    params = {
        "filter[user_id][_eq]": user_id,
        "offset": offset,
        "limit": limit,
        "sort": "id",
        # where trash_at is NULL and is_active is True
        "filter[is_active][_eq]":True,
        "filter[trashed_at][_null]":True
    }
    posts_data = await directus_client.list("posts", params=params)
    return [_to_post(item, owner=user) for item in posts_data] if posts_data else []

async def get_post_by_id_from_database(id: int) -> Post | None:
    org_id = get_current_org_id()
    post = await directus_client.get_by_id(
        "posts", 
        id
        )
    if not post:
        return None

    if post.get("trashed_at") is not None or post.get("is_active") is False:
        return None

    user = await find_user_by_id(post["user_id"])
    if not user:
        return None
    if org_id and str(user.organization_id) != str(org_id):
        return None

    return _to_post(post, owner=user)

async def update_post_by_id_in_database(id: int, data: UpdatePostRequest) -> Post | None:
    post = await get_post_by_id_from_database(id)
    if not post:
        return None
    payload = {}
    if data.title is not None:
        payload["title"] = data.title
    if data.content is not None:
        payload["content"] = data.content
    if payload:
        payload["updated_at"] = datetime.now(UTC).isoformat()
        updated = await directus_client.update("posts", str(id), payload)
        return _to_post(updated, owner=post.owner_id)
    return post

async def delete_post_by_id_from_database(id: int) -> Post | None:
    post = await get_post_by_id_from_database(id)
    if not post:
        return None

    # We are passing these payload to update the post. Instead of deleting it, is_active is turned False. 
    payload = {
        "trashed_at": datetime.now(UTC).isoformat(),
        "is_active":False
    }
    updated = await directus_client.update("posts", str(id), payload)
    return _to_post(updated, owner=post.owner_id)
