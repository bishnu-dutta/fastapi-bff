from typing import Annotated

from fastapi import APIRouter, Query, status

from app.auth.helpers import CurrentUser

from .request import CreateUserRequest, UpdateUserRequest
from .response import PrivateUserResponse, PublicUserResponse
from .service import (
    create_user,
    delete_user,
    get_all_users,
    get_user_by_id,
    update_user,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/create", 
    response_model=PrivateUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create and saves a new user to database"
)
async def create_user_api(data: CreateUserRequest):
    return await create_user(data)


@router.get("/all", 
    response_model=list[PublicUserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    description="Get all list of users from database(only public accessible data)",
)
async def get_all_users_api(
    current_user: CurrentUser,
    offset: Annotated[int,Query(ge=0)] = 0,
    limit:  Annotated[int,Query(ge=1,le=100)] = 100
):
    return await get_all_users(current_user,offset,limit)


@router.get("/{id}", 
    response_model=PublicUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a user by id",
    description="Get a user by id from database(only public accessible data)"
)
async def get_user_by_id_api(id: int, current_user: CurrentUser):
    return await get_user_by_id(id, current_user)


@router.delete("/delete", 
    response_model=PrivateUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete current user",
    description="Delete current user data from database(only the current authorised user can delete itself)"
)
async def delete_user_api(current_user: CurrentUser):
    return await delete_user(current_user)


@router.put("/update", 
    response_model=PrivateUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user",
    description="Update current user data from database(only the current authorised user can update itself)"
)
async def update_user_api(data: UpdateUserRequest, current_user: CurrentUser):
    return await update_user(current_user, data)


# @router.post("/forgot-password", 
#     response_model=MessageResponse, 
#     status_code=status.HTTP_200_OK, 
#     summary="request password reset", 
#     description="Forgot password of a user, sends a password reset link to the user's email if verified"
# )
# async def forgot_password_api(data: ForgotPasswordRequest):
#     return await send_forgot_password_link(data.email)


# @router.post("/reset-password/{token}",
#     response_model=MessageResponse,
#     status_code=status.HTTP_200_OK,summary="Reset password",
#     description="Reset password of a user if the user is verified and token is valid"
# )
# async def reset_password_api(token:str, data: ResetPasswordRequest):
#     return await reset_password_with_token(token, data)
