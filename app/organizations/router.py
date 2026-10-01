from typing import Annotated

from fastapi import APIRouter, Query, status

from app.middleware.role_scope import admin
from app.models import User
from app.posts.request import CreatePostRequest, UpdatePostRequest
from app.posts.response import PrivatePostResponse, UpdatePrivatePostResponse
from app.posts.service import get_all_posts
from app.users.request import UpdateUserRequest
from app.users.response import PrivateUserResponse
from app.users.service import get_all_users, get_user_by_id

from .request import AdminCreateUserRequest
from .service import (
    admin_add_user,
    admin_create_post_for_user,
    admin_delete_post_by_id_of_user,
    admin_delete_user_by_id,
    admin_get_all_posts_of_user,
    admin_get_posts_by_id_of_user,
    admin_update_post_by_id_of_user,
    admin_update_user_by_id
)

router = APIRouter(prefix="/admin", tags=["organizations"], dependencies=[admin])

# ------ USER ------
@router.post("/user", 
            response_model=PrivateUserResponse,
            status_code=status.HTTP_201_CREATED, 
            summary="Create a new user by admin", 
            description="Create a new user in org by admin"
            )

async def admin_create_user(
    data: AdminCreateUserRequest,
    current_user: User = admin

):
    return await admin_add_user(data, current_user)
    
@router.get("/all", 
            response_model=list[PrivateUserResponse],
            status_code=status.HTTP_200_OK, 
            summary="Get all users", 
            description="Get all list of users of current organization from database(only admin accessible data)"
            )

async def admin_get_all_users_api(
    current_user: User = admin,
    offset: Annotated[int,Query(ge=0)] = 0,
    limit:  Annotated[int,Query(ge=1,le=100)] = 100
):
    return await get_all_users(current_user, offset, limit)  

@router.get("/{id}", 
            response_model=PrivateUserResponse, 
            status_code=status.HTTP_200_OK, 
            summary="Get a user by id", 
            description="Get a user by id of current organization from database(only admin accessible data)"
            )

async def admin_get_user_by_id_api(
    id: int,
    current_user: User = admin,
):
    return await get_user_by_id(id, current_user)

@router.put("/{id}",
            response_model=PrivateUserResponse,
            status_code=status.HTTP_200_OK,
            summary="Update a user by id",
            description="Update a user by id of current organization from database(only admin accessible data)"
)
async def admin_update_user_api(
    id: int,
    data: UpdateUserRequest,
    current_user: User = admin,
):
    return await admin_update_user_by_id(id, data, current_user)

@router.delete("/{id}", 
            response_model=PrivateUserResponse,
            status_code=status.HTTP_200_OK,
            summary="Delete a user by id",
            description="Delete a user by id from current organization from database(only admin accessible data)"
)
async def admin_delete_user_api(
    id: int,
    current_user: User = admin,
):
    return await admin_delete_user_by_id(id, current_user)


# ------ POST ------

@router.get("/posts/all", 
            response_model=list[PrivatePostResponse],
            status_code=status.HTTP_200_OK, 
            summary="Get all posts", 
            description="Get all list of posts of current organization from database(only admin accessible data)"
            )
async def admin_get_all_posts_api(
    current_user: User = admin,
    offset: Annotated[int,Query(ge=0)] = 0,
    limit:  Annotated[int,Query(ge=1,le=100)] = 100,

):
    return await get_all_posts(current_user, offset, limit)

@router.get("/posts/user/{id}", 
            response_model=list[PrivatePostResponse],
            status_code=status.HTTP_200_OK, 
            summary="Get all posts of a user", 
            description="Get all list of posts of a user of current organization from database(only admin accessible data)"
            )
async def admin_get_all_posts_of_user_api(
    id: int,
    current_user: User = admin,
    offset: Annotated[int,Query(ge=0)] = 0,
    limit:  Annotated[int,Query(ge=1,le=100)] = 100
):
    return await admin_get_all_posts_of_user(id, current_user, offset, limit)

@router.post("/posts/user/{id}",
            response_model=PrivatePostResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create a new post for a user by admin",
            description="Create a new post for a user of current organization from database(only admin accessible data)"
)
async def admin_create_post_api(
    id: int,
    data: CreatePostRequest,
    current_user: User = admin,
):
    return await admin_create_post_for_user(id, data, current_user)

@router.get("/posts/user/{owner_id}/post/{post_id}", 
            response_model=PrivatePostResponse,
            status_code=status.HTTP_200_OK, 
            summary="Get a post by id", 
            description="Get a post by id of a user of current organization from database(only admin accessible data)"
            )
async def admin_get_post_by_id_api(
    owner_id:int,
    post_id: int,
    current_user: User = admin,
):
    return await admin_get_posts_by_id_of_user(owner_id,post_id,current_user)


@router.put("/posts/user/{owner_id}/post/{post_id}",
            response_model=UpdatePrivatePostResponse,
            status_code=status.HTTP_200_OK,
            summary="Update a post by id",
            description="Update a post by id of current organization from database(only admin accessible data)"
)
async def admin_update_post_api(
    owner_id:int,
    post_id: int,
    data: UpdatePostRequest,
    current_user: User = admin,
):
    return await admin_update_post_by_id_of_user(owner_id, post_id, data, current_user)

@router.delete("/posts/user/{owner_id}/post/{post_id}", 
            response_model=PrivatePostResponse,
            status_code=status.HTTP_200_OK,
            summary="Delete a post by id",
            description="Delete a post by id from current organization from database(only admin accessible data)"
)
async def admin_delete_post_api(
    owner_id:int,
    post_id: int,
    current_user: User = admin
):
    return await admin_delete_post_by_id_of_user(owner_id, post_id, current_user)

