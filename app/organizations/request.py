from pydantic import BaseModel, EmailStr, Field

from app.models import UserRole


class AdminCreateUserRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
        description="Unique username for the new member"
        )
    email: EmailStr = Field(
        min_length=5,
        max_length=255,
        description="Corporate email address for the new member"
        )
    password: str = Field(
        min_length=8,
        description="Initial temporary or permanent password"
        )
    first_name: str = Field(
        min_length=1,
        max_length=50,
        description="First name of the new member"
        )
    last_name: str = Field(
        min_length=1,
        max_length=50,
        description="Last name of the new member"
        )
    role: UserRole = Field(
        default = UserRole.USER,
        description="Organizational role assigned to the new user"
        )
