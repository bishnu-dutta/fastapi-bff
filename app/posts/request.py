from pydantic import BaseModel, Field


class CreatePostRequest(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
        description="Title of the post"
    )
    content: str = Field(
        min_length=1,
        max_length=50000,
        description="Content of the post"
    )

class UpdatePostRequest(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Title of the post"
    )
    content: str | None = Field(
        default=None,
        min_length=1,
        max_length=50000,
        description="Content of the post"
    )