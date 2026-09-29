
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.context import get_current_org_id, get_current_session
from app.models import Post, User
from app.posts.request import CreatePostRequest, UpdatePostRequest


async def admin_save_post_for_user_to_database(data: CreatePostRequest, user_id: int) -> Post:
    session = get_current_session()
    post = Post(
        user_id=user_id,
        title=data.title,
        content=data.content,
        created_at=datetime.now(UTC),
    )
    session.add(post)
    await session.commit()
    await session.refresh(post, attribute_names=["owner_id"])
    return post

async def admin_get_user_post_by_id_from_database(user_id: int, post_id: int) -> Post | None:
    org_id = get_current_org_id()
    session = get_current_session()
    query = select(Post).options(joinedload(Post.owner_id)).where(Post.id == post_id, Post.user_id == user_id)
    if org_id:
        query = query.join(User, Post.user_id == User.id).where(User.organization_id == org_id)
    result = await session.execute(query)
    return result.scalars().first()


async def admin_update_post_by_id_in_database(user_id: int, post_id: int, data: UpdatePostRequest) -> Post | None:
    post = await admin_get_user_post_by_id_from_database(user_id, post_id)
    session = get_current_session()
    if post:
        if data.title is not None:
            post.title = data.title
        if data.content is not None:
            post.content = data.content
        post.updated_at = datetime.now(UTC)
        await session.commit()
        await session.refresh(post, attribute_names=["owner_id"])
    return post

async def admin_delete_post_by_id_from_database(user_id: int, post_id: int) -> Post | None:
    post = await admin_get_user_post_by_id_from_database(user_id, post_id)
    session = get_current_session()
    if post:
        await session.delete(post)
        await session.commit()
    return post

