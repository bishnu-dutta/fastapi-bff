
from datetime import UTC, datetime

from app.core.context import get_current_org_id
from app.models import Post, User
from app.posts.request import CreatePostRequest, UpdatePostRequest
from app.services.directus import _to_post, directus_client
from app.users.repository import find_user_by_id


async def admin_save_post_for_user_to_database(data: CreatePostRequest, user_id: int, user:User) -> Post:
    payload = {
        "user_id":user_id,
        "title":data.title,
        "content":data.content,
        "created_at": datetime.now(UTC).isoformat(),
    }
    post = await directus_client.create("posts", payload)
    return _to_post(post, owner=user)




async def admin_get_user_post_by_id_from_database(user_id: int, post_id: int) -> Post | None:
    org_id = get_current_org_id()

    user = await find_user_by_id(user_id)
    if not user:
        return None
    if org_id and str(user.organization_id) != str(org_id):
        return None

    post = await directus_client.get_by_id("posts", post_id)
    if not post:
        return None
    post_user_id = post.get("user_id")
    if isinstance(post_user_id, dict):
        post_user_id = post_user_id.get("id")

    if post_user_id != user_id:
        return None

    # Map to Post model and attach the user as owner
    return _to_post(post, owner=user)


async def admin_update_post_by_id_in_database(user_id: int, post_id: int, data: UpdatePostRequest) -> Post | None:
    post = await admin_get_user_post_by_id_from_database(user_id, post_id)
    if not post:
        return None 
    payload = {}
    if data.title is not None:
        payload["title"] = data.title
    if data.content is not None:
        payload["content"] = data.content
    if payload:
        payload["updated_at"] = datetime.now(UTC).isoformat()
        updated = await directus_client.update("posts", str(post_id), payload)
        return _to_post(updated, owner=post.owner_id)
    return post


async def admin_delete_post_by_id_from_database(user_id: int, post_id: int) -> Post | None:
    post = await admin_get_user_post_by_id_from_database(user_id, post_id)
    if post:
        await directus_client.delete("posts", str(post_id))
    return post

