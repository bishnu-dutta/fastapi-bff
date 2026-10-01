from typing import Optional
from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_expires_in: Optional[int] = None

    class Config:
        extra = "ignore"  # Keycloak's token response has extra fields we don't need
class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

