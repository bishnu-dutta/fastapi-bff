from app.models import UserRole
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from fastapi_mail import MessageSchema, MessageType

from app.auth.helpers import CurrentUser
from app.auth.service import (
    create_password_reset_token,
    verify_password,
    verify_reset_token,
)
from app.core.context import get_current_session
from app.utils.mail import generate_otp, get_otp_expiry, mail

from .repository import (
    all_users,
    delete_user_by_id,
    find_user_by_email,
    find_user_by_id,
    save_user_to_database,
    update_password_by_email,
    update_user_by_id,
    update_user_otp,
)
from .request import CreateUserRequest, ResetPasswordRequest, UpdateUserRequest


async def create_user(data: CreateUserRequest):
    existing_user = await find_user_by_email(data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    p_otp, h_otp = generate_otp()
    otp_expiry = get_otp_expiry(minutes=10)
    user = await save_user_to_database(
        data, 
        h_otp, 
        otp_expiry, 
        role=UserRole.USER, 
        organization_id=data.organization_id)
    await send_otp_email(user.email, p_otp)
    return user


async def send_otp_email(recipient_email: str, otp: str, subject: str = "Verify your account"):
    
    html_content = f"""
    <h2>Account Verification</h2>
    <p>Your 6-digit verification code is:</p>
    <h1 style="letter-spacing: 4px; color: #2563eb;">{otp}</h1>
    <p>This code will expire in 10 minutes.</p>
    """
    message = MessageSchema(
        subject=subject,
        recipients=[recipient_email],
        body=html_content,
        subtype=MessageType.html,
    )
    await mail.send_message(message)

async def verify_otp(email:str,otp:str):
    user = await find_user_by_email(email)
    session = get_current_session()
    if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
    if user.is_verified:
        return {"message": "Account is already verified"}

    if user.otp_attempts >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please request a new OTP.",
        )

    if not user.otp_expiry or datetime.now(UTC) > user.otp_expiry.replace(tzinfo=UTC):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one.",
        )
    if not user.otp_hash or not verify_password(otp, user.otp_hash):
        user.otp_attempts += 1
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP code. Remaining attempts: {5 - user.otp_attempts}",
        )

    user.is_verified = True
    user.otp_hash = None
    user.otp_expiry = None
    user.otp_attempts = 0
    await session.commit()
    return {"message": "Account verified successfully. You can now log in."}

async def resend_otp(email:str):
    user = await find_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already verified",
        )

    if user.otp_expiry:
        last_sent = user.otp_expiry.replace(tzinfo=UTC) - timedelta(minutes=10)
        if (datetime.now(UTC) - last_sent).total_seconds() < 60:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Please wait at least 60 seconds before requesting another OTP.",
            )
    # Generate new OTP & hash
    p_otp, h_otp = generate_otp()
    otp_expiry = get_otp_expiry(minutes=10)
    await update_user_otp(user,h_otp,otp_expiry)
    await send_otp_email(user.email,p_otp,"Your new verification code")
    return {"message": "A new verification code has been sent to your email."}



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
    return user


async def update_user(current_user: CurrentUser, data: UpdateUserRequest):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this user",
        )
        
    if data.email is not None:
        new_email = data.email.lower()
        if new_email != current_user.email:
            existing_user = await find_user_by_email(new_email)
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email is already registered with another account.",
                )

    user = await update_user_by_id(current_user.id, data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


async def send_forgot_password_link(email:str):

    reset_token = await create_password_reset_token(email)

    reset_link = f"http://localhost:8000/users/reset-password/{reset_token}"

    html_content = f"""
    <h2>Reset Your Password</h2>
    <p>Click the link below to set a new password. This link is valid for 15 minutes:</p>
    <p><a href="{reset_link}" style="padding: 10px 16px; background-color: #2563eb; color: #fff; text-decoration: none; border-radius: 4px;">Reset Password</a></p>
    <p>If you didn't request this, you can safely ignore this email.</p>
    """

    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=html_content,
        subtype=MessageType.html,
    )
    await mail.send_message(message)

    return {"message" : "A password reset link has been sent."}


async def reset_password_with_token(token:str, passwords:ResetPasswordRequest):
    mail_ID = await verify_reset_token(token)

    if not mail_ID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    user_mail = await find_user_by_email(mail_ID)
    
    if not user_mail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mail not found",
        )
    
    if not user_mail.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is not verified",
        )

    new_password = passwords.new_password
    confirm_password = passwords.confirm_password

    if new_password != confirm_password:
        raise HTTPException(
            detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
        )
        
    await update_password_by_email(user_mail, new_password)

    return {"message" : "Password reset successfully"}