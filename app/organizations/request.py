from pydantic import BaseModel, EmailStr

from app.models import UserRole


class AdminCreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str 
    role: UserRole = UserRole.USER
