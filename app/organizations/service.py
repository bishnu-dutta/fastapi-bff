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
from app.services.directus import logger
from app.services.keycloak import (
    create_keycloak_user,
    delete_keycloak_user,
    update_keycloak_user,
)
from app.users.repository import (
    delete_user_by_id,
    find_user_by_email,
    find_user_by_email_and_username,
    find_user_by_id,
    find_user_by_username,
    save_user_to_database,
    update_user_by_id,
)
from app.users.request import (
    UpdateUserRequest,
)

from .repository import admin_get_user_post_by_id_from_database

# ------ USER ------

async def admin_add_user(data: AdminCreateUserRequest, admin_user: User):
    existing_user = await find_user_by_email_and_username(data.email, data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )
    keycloak_sub = create_keycloak_user(data, admin_user.organization_id, data.role)


    try:
        user = await save_user_to_database(
            data,
            keycloak_sub,
            organization_id=admin_user.organization_id,
            role=data.role,
        )
    # blind exception, fix later
    except Exception as exc: 
        delete_keycloak_user(keycloak_sub)

        # If Directus already raised an HTTPException, preserve and re-raise it
        if isinstance(exc, HTTPException):
            raise
        
        # Otherwise it's an unexpected Python error: log the traceback and return 500
        logger.exception("Failed to save user in database for keycloak_sub: %s", keycloak_sub)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save user in database: {exc}",
        ) from exc
    return user
    

async def admin_update_user_by_id(id: int, data: UpdateUserRequest, admin_user: User):

    user = await find_user_by_id(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in your organization")

    # email duplicate check
    if data.email is not None:
        new_email = data.email.lower()
        existing_user = await find_user_by_email(new_email)
        if existing_user and existing_user.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered with another account.",
            )

    # username duplicate check
    if data.username is not None:
        new_username = data.username
        if new_username != user.username:
            existing_user = await find_user_by_username(new_username)
            if existing_user and existing_user.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username is already taken by another account.",
                )
            
    # update keycloak
    if user.keycloak_sub:
        update_keycloak_user(
            str(user.keycloak_sub),
            data.model_dump(exclude_unset=True)
        )

    # update directus
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
        
    if user.keycloak_sub:
        delete_keycloak_user(user.keycloak_sub)    
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
    return await admin_save_post_for_user_to_database(data, user.id, user)


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

