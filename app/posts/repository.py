from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.context import get_current_org_id, get_current_session
from app.models import Post, User

from .request import CreatePostRequest, UpdatePostRequest


async def save_post_to_database(data: CreatePostRequest, current_user_id: int):
    session = get_current_session()
    post = Post(
        user_id=current_user_id,
        title=data.title,
        content=data.content,
        created_at=datetime.now(UTC),
    )
    session.add(post)
    await session.commit()
    await session.refresh(post, attribute_names=["owner_id"])
    return post

async def get_all_posts_from_database(offset:int,limit:int) -> list[Post]:
    session = get_current_session()
    org_id = get_current_org_id()
    result = select(Post).options(joinedload(Post.owner_id)).offset(offset).limit(limit).order_by(Post.id.asc())
    if org_id:
        result = result.join(User, Post.user_id == User.id).where(User.organization_id == org_id)
    result = await session.execute(result)
    return list(result.scalars().all())

async def get_all_post_by_user_id_from_database(user_id: int,offset:int,limit:int) -> list[Post]:
    session = get_current_session()
    org_id = get_current_org_id()
    result = select(Post).options(joinedload(Post.owner_id)).where(Post.user_id == user_id).offset(offset).limit(limit).order_by(Post.id.asc())
    if org_id:
        result = result.join(User, Post.user_id == User.id).where(User.organization_id == org_id)
    result = await session.execute(result)
    return list(result.scalars().all())

async def get_post_by_id_from_database(id: int) -> Post | None:
    session = get_current_session()
    org_id = get_current_org_id()
    result = select(Post).options(joinedload(Post.owner_id)).where(Post.id == id)
    if org_id:
        result = result.join(User, Post.user_id == User.id).where(User.organization_id == org_id)
    result = await session.execute(result)
    return result.scalars().first()

async def update_post_by_id_in_database(id: int, data: UpdatePostRequest) -> Post | None:
    session = get_current_session()
    post = await get_post_by_id_from_database(id)
    if post:
        if data.title is not None:
            post.title = data.title
        if data.content is not None:
            post.content = data.content
        post.updated_at = datetime.now(UTC)
        await session.commit()
        await session.refresh(post, attribute_names=["owner_id"])
    return post

async def delete_post_by_id_from_database(id: int) -> Post | None:
    session = get_current_session()
    post = await get_post_by_id_from_database(id)
    if post:
        await session.delete(post)
        await session.commit()
    return post
