import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class PublicUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    
class PrivateUserResponse(PublicUserResponse):
    email: EmailStr
    organization_id: uuid.UUID
    role: str
    organization_name: str | None
    # all_posts: list[PublicPostResponse] = [] 

class MessageResponse(BaseModel):
    message : str


    