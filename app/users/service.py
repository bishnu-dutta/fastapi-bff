from fastapi import HTTPException, status

from app.auth.helpers import CurrentUser
from app.models import UserRole
from app.services.keycloak import (
    KeycloakError,
    create_keycloak_user,
    delete_keycloak_user,
    update_keycloak_user,
)
from app.users.request import UpdateUserRequest

from .repository import (
    all_users,
    delete_user_by_id,
    find_user_by_email,
    find_user_by_email_and_username,
    find_user_by_id,
    find_user_by_username,
    save_user_to_database,
    update_user_by_id,
)
from .request import CreateUserRequest


async def create_user(data: CreateUserRequest):
    existing_user = await find_user_by_email_and_username(data.email, data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )
    try:
        keycloak_sub = create_keycloak_user(data, data.organization_id)
    except KeycloakError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    try:
        user = await save_user_to_database(
            data,
            keycloak_sub,
            organization_id=data.organization_id,
            role=UserRole.USER,
        )
    except Exception:  # noqa: BLE001
        delete_keycloak_user(keycloak_sub)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{data.organization_id}' not found",
        )
    return user



async def get_all_users(current_user: CurrentUser,offset,limit):
    users = await all_users(offset, limit)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Users not found",
        )
    return users


async def get_user_by_id(id: int, current_user: CurrentUser):
    user = await find_user_by_id(id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


async def delete_user(current_user: CurrentUser):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this user",
        )
    user = await delete_user_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user.keycloak_sub:
        try:
            delete_keycloak_user(user.keycloak_sub)
        except KeycloakError as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)    
    return user


async def update_user(current_user: CurrentUser, data: UpdateUserRequest):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this user",
        )

    # email duplicate check
    if data.email is not None:
        new_email = data.email.lower()
        if new_email != current_user.email:
            existing_user = await find_user_by_email(new_email)
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email is already registered with another account.",
                )

    # username duplicate check
    if data.username is not None:
        new_username = data.username
        if new_username != current_user.username:
            existing_user = await find_user_by_username(new_username)
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username is already taken by another account.",
                )

    # update keycloak
    if current_user.keycloak_sub:
        try:
            update_keycloak_user(
                str(current_user.keycloak_sub),
                data.model_dump(exclude_unset=True)
            )
        except KeycloakError as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)

    # update directus
    user = await update_user_by_id(current_user.id, data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


# async def send_forgot_password_link(email:str):

#     reset_token = await create_password_reset_token(email)

#     reset_link = f"http://localhost:8000/users/reset-password/{reset_token}"

#     html_content = f"""
#     <h2>Reset Your Password</h2>
#     <p>Click the link below to set a new password. This link is valid for 15 minutes:</p>
#     <p><a href="{reset_link}" style="padding: 10px 16px; background-color: #2563eb; color: #fff; text-decoration: none; border-radius: 4px;">Reset Password</a></p>
#     <p>If you didn't request this, you can safely ignore this email.</p>
#     """

#     message = MessageSchema(
#         subject="Password Reset Request",
#         recipients=[email],
#         body=html_content,
#         subtype=MessageType.html,
#     )
#     await mail.send_message(message)

#     return {"message" : "A password reset link has been sent."}


# async def reset_password_with_token(token:str, passwords:ResetPasswordRequest):
#     mail_ID = await verify_reset_token(token)

#     if not mail_ID:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or expired token",
#         )

#     user = await find_user_by_email(mail_ID)
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Mail not found",
#         )
    
#     if not user.is_verified:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Account is not verified",
#         )

#     new_password = passwords.new_password
#     confirm_password = passwords.confirm_password

#     if new_password != confirm_password:
#         raise HTTPException(
#             detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
#         )
        
#     await update_password_by_email(user, new_password)

#     return {"message" : "Password reset successfully"}