from app.utils.mail import generate_otp, get_otp_expiry
from fastapi import HTTPException, status

from app.models import User
from app.organizations.repository import (
    admin_delete_post_by_id_from_database,
    admin_save_post_for_user_to_database,
    admin_update_post_by_id_in_database,
)
from app.organizations.request import AdminCreateUserRequest
from app.posts.repository import get_all_post_by_user_id_from_database
from app.posts.request import CreatePostRequest, UpdatePostRequest
from app.users.repository import (
    delete_user_by_id,
    find_user_by_email,
    find_user_by_id,
    update_user_by_id,
    save_user_to_database
)
from app.users.request import (
    UpdateUserRequest,
)
from app.users.service import send_otp_email

from .repository import admin_get_user_post_by_id_from_database

# ------ USER ------

async def admin_add_user(data: AdminCreateUserRequest, admin_user: User):
    existing_user = await find_user_by_email(data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
        detail="User already exists"
        )
    p_otp, h_otp = generate_otp()
    otp_expiry = get_otp_expiry(minutes=10)
    user = await save_user_to_database(
        data, 
        h_otp, 
        otp_expiry, 
        role=data.role, 
        organization_id=admin_user.organization_id
        )
    await send_otp_email(user.email, p_otp)
    return user
    

async def admin_update_user_by_id(id: int, data: UpdateUserRequest, admin_user: User):

    if data.email is not None:
        new_email = data.email.lower()
        existing_user = await find_user_by_email(new_email)
        if existing_user and existing_user.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered with another account.",
            )
    user = await update_user_by_id(id, data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

async def admin_delete_user_by_id(id: int, admin_user: User):
    if admin_user.id == id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Use self-delete endpoint to delete your own account")
        
    user = await delete_user_by_id(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in your organization")
    return user


# ------ POST ------
async def admin_get_all_posts_of_user(owner_id:int, current_user: User,offset:int,limit:int):
    posts = await get_all_post_by_user_id_from_database(owner_id,offset,limit)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found in your organization")
    return posts

async def admin_create_post_for_user(user_id: int,data: CreatePostRequest,admin_user: User):
    user = await find_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in your organization"
        )
    return await admin_save_post_for_user_to_database(data, user_id=user.id)


async def admin_get_posts_by_id_of_user(owner_id:int,post_id:int,current_user: User):
    posts = await admin_get_user_post_by_id_from_database(user_id=owner_id,post_id=post_id)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found in your organization")
    return posts

async def admin_update_post_by_id_of_user(owner_id:int, post_id:int, data: UpdatePostRequest, current_user: User):
    posts = await admin_update_post_by_id_in_database(user_id=owner_id,post_id=post_id, data=data)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found in your organization")
    return posts

async def admin_delete_post_by_id_of_user(owner_id:int,post_id:int,current_user: User):
    posts = await admin_delete_post_by_id_from_database(user_id=owner_id,post_id=post_id)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found in your organization")
    return posts

