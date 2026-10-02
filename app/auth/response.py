
from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int | None = None
    refresh_expires_in: int | None = None

    class Config:
        extra = "ignore"  # Keycloak's token response has extra fields we don't need
class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

