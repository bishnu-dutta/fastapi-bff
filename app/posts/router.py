from typing import Annotated

from fastapi import APIRouter, Query, status

from app.auth.helpers import CurrentUser
from app.posts.response import UpdatePrivatePostResponse

from .request import CreatePostRequest, UpdatePostRequest
from .response import PrivatePostResponse, PublicPostResponse
from .service import (
    create_post,
    delete_post_by_id,
    get_all_posts,
    get_all_posts_of_user,
    get_post_by_id,
    update_post_by_id,
)

router = APIRouter(prefix="/user/post", tags=["posts"])

@router.post("/create", 
    response_model=PrivatePostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
    description="Create and saves a new post authored by the currently authenticated user"
    )
async def create_post_api(
    data: CreatePostRequest,
    current_user: CurrentUser
):
    return await create_post(data, current_user)

@router.get("/all-posts", 
    response_model=list[PublicPostResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all public posts",
    description="Get all posts from all users(only public accessible data)"
    )
async def get_all_posts_api(
    current_user: CurrentUser,
    offset: Annotated[int,Query(ge=0)] = 0,
    limit:  Annotated[int,Query(ge=1,le=100)] = 100
):
    return await get_all_posts(current_user,offset,limit)

@router.get("/all", 
    response_model=list[PrivatePostResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all posts of the current user",
    description="Get all posts created by the current authenticated user(includes all datas)"
    )
async def get_all_posts_of_user_api(
    current_user: CurrentUser,
    offset: Annotated[int,Query(ge=0)] = 0,
    limit:  Annotated[int,Query(ge=1,le=100)] = 100
):
    return await get_all_posts_of_user(current_user,offset,limit)
    
@router.get("/{id}",
    response_model=PrivatePostResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a post by id",
    description="Get a post owned by the current authenticated user(includes all data)"
    )
async def get_post_by_id_api(
    id: int,
    current_user: CurrentUser
):
    return await get_post_by_id(id, current_user)


@router.put("/{id}", 
    response_model=UpdatePrivatePostResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a post by id",
    description="Update a post owned by the current authenticated user"
    )
async def update_post_by_id_api(
    id: int,
    data: UpdatePostRequest,
    current_user: CurrentUser
):
    return await update_post_by_id(id, current_user, data)

@router.delete("/{id}", 
    response_model=PrivatePostResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a post by id",
    description="Delete a post owned by the current authenticated user"
    )
async def delete_post_by_id_api(
    id: int,
    current_user: CurrentUser
):
    return await delete_post_by_id(id, current_user)
