
import uuid

from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str 
    first_name: str
    last_name: str
    organization_id: uuid.UUID


class UpdateUserRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")

class ResendOTPRequest(BaseModel):
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    new_password: str
    confirm_password: str
