from pydantic import BaseModel, EmailStr

from app.models import UserRole


class AdminCreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str 
    first_name: str
    last_name: str  
    role: UserRole = UserRole.USER
