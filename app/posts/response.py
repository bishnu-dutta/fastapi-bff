from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class PublicPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    content: str
    user_id : int
    created_at: datetime 

class PrivatePostResponse(PublicPostResponse):
    model_config = ConfigDict(from_attributes=True)
    author: EmailStr

class UpdatePrivatePostResponse(PrivatePostResponse):
    updated_at: datetime
    