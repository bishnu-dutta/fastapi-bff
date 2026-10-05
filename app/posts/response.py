from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PublicPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(
        description="Unique identifier for the post.(auto-incrementing)"
        )
    title: str = Field(
        description="Title of the post"
        )
    content: str = Field(
        description="Content of the post"
        )
    user_id : int = Field(
        description="Unique identifier for the user who created the post"
        )
    created_at: datetime = Field(
        description="Timestamp (UTC) when the post was created"
        ) 

class PrivatePostResponse(PublicPostResponse):
    model_config = ConfigDict(from_attributes=True)
    author: EmailStr = Field(
        description="Email of post's author"
        )

class UpdatePrivatePostResponse(PrivatePostResponse):
    model_config = ConfigDict(from_attributes=True)
    updated_at: datetime = Field(
        description="Timestamp (UTC) when the post was last modified"
        )
    