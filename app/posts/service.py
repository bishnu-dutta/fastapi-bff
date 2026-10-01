from fastapi import HTTPException, status

from app.auth.helpers import CurrentUser

from .repository import (
    delete_post_by_id_from_database,
    get_all_post_by_user_id_from_database,
    get_all_posts_from_database,
    get_post_by_id_from_database,
    save_post_to_database,
    update_post_by_id_in_database,
)
from .request import CreatePostRequest, UpdatePostRequest


async def create_post(data: CreatePostRequest, current_user: CurrentUser):
    return await save_post_to_database(data, current_user.id,current_user)
    

async def get_all_posts(current_user: CurrentUser,offset,limit):
    posts = await get_all_posts_from_database(offset,limit)
    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts found",
        )
    return posts

async def get_all_posts_of_user(current_user: CurrentUser,offset:int = 0,limit:int = 10):
    posts = await get_all_post_by_user_id_from_database(current_user.id,offset,limit)
    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts found",
        )
    for post in posts:
        if post.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to get these posts",
            )
    return posts

async def get_post_by_id(id: int, current_user: CurrentUser):
    post = await get_post_by_id_from_database(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to get this post",
        )
    return post

async def update_post_by_id(id: int, current_user: CurrentUser, data: UpdatePostRequest):
    post = await get_post_by_id_from_database(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this post",
        )
    post = await update_post_by_id_in_database(id, data)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return post

async def delete_post_by_id(id: int, current_user: CurrentUser):
    post = await get_post_by_id_from_database(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this post",
        )
    post = await delete_post_by_id_from_database(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return post