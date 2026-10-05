import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PublicUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(
        description="Unique identifier for the user"
        )
    username: str = Field(
        description="Unique username handle for authentication and display"
        )
    
class PrivateUserResponse(PublicUserResponse):
    email: EmailStr = Field(
        description="Registered email address of the user"
        )
    organization_id: uuid.UUID = Field(
        description="UUID of the organization the user belongs to"
        )
    role: str = Field(
        description="Role and permission scope assigned to the user (e.g. user, org_admin, super_admin)"
        )
    organization_name: str | None = Field(
        default = None,
        description="Name of the organization the user belongs to"
        )
    # all_posts: list[PublicPostResponse] = [] 

# class MessageResponse(BaseModel):
#     message : str


    