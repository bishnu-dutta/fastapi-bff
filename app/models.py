import uuid
from datetime import datetime
from enum import StrEnum

from dataclasses import dataclass, field

class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    USER = "user"

@dataclass
class Organization:
    name: str 
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    user_org: list["User"] = field(default_factory=list)


@dataclass
class User:
    id: int 
    username: str 
    email: str 
    hashed_password: str
    organization_id: uuid.UUID 
    is_verified: bool = False
    otp_hash: str | None = None
    otp_expiry: datetime | None = None
    otp_attempts: int = 0
    organization: Organization | None = None
    role: UserRole | str = UserRole.USER
    posts: list["Post"] = field(default_factory=list)
    @property
    def organization_name(self) -> str | None:
        return self.organization.name if self.organization else None
    @property
    def all_posts(self) -> list["Post"]:
        return self.posts

@dataclass
class Post:
    id: int 
    title: str 
    content: str 
    user_id: int 
    created_at: datetime 
    owner_id: User | None = None
    updated_at: datetime | None = None
    @property
    def author(self) -> str | None:
        return self.owner_id.email if self.owner_id else None


