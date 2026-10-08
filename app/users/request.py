
import uuid

from pydantic import BaseModel, EmailStr, Field


class CreateUserRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
        description="Unique username handle for authentication and display"
        )
    email: EmailStr = Field(
        min_length=5,
        max_length=255,
        description="Primary email address used for login and notifications"
        )
    password: str = Field(
        min_length=8,
        description="Account password (minimum 8 characters)"
        )
    first_name: str = Field(
        min_length=1,
        max_length=50,
        description="User's preferred first name"
        )
    last_name: str = Field(
        min_length=1,
        max_length=50,
        description="User's preferred last name"
        )
    organization_id: uuid.UUID = Field(
        description="UUID of the organization this user is registered under"
        )


class UpdateUserRequest(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
        description="Unique username handle for authentication and display"
        )
    email: EmailStr | None = Field(
        default=None,
        min_length=5,
        max_length=255,
        description="Primary email address used for login and notifications"
        )
    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="User's preferred first name"
        )
    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="User's preferred last name"
        )

    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    
    
class ResendVerificationMailRequest(BaseModel):
    email: EmailStr

# class OTPVerify(BaseModel):
#     email: EmailStr
#     otp: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")

# class ResendOTPRequest(BaseModel):
#     email: EmailStr

# class ForgotPasswordRequest(BaseModel):
#     email: EmailStr

# class ResetPasswordRequest(BaseModel):
#     new_password: str
#     confirm_password: str
