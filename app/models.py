import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    USER = "user"

@dataclass(kw_only=True)
class BaseMixin:
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None
    trashed_at: datetime | None = None

@dataclass(kw_only=True)
class Organization(BaseMixin):
    name: str 
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    user_org: list[User] = field(default_factory=list)


@dataclass(kw_only=True)
class User(BaseMixin):
    id: int 
    username: str 
    email: str 
    first_name: str
    last_name: str
    keycloak_sub: uuid.UUID
    organization_id: uuid.UUID 
    is_verified: bool = False
    # hashed_password: str
    # otp_hash: str | None = None
    # otp_expiry: datetime | None = None
    # otp_attempts: int = 0
    organization: Organization | None = None
    role: UserRole | str = UserRole.USER
    posts: list[Post] = field(default_factory=list)
    @property
    def organization_name(self) -> str | None:
        return self.organization.name if self.organization else None
    @property
    def all_posts(self) -> list[Post]:
        return self.posts

@dataclass(kw_only=True)
class Post(BaseMixin):
    id: int 
    title: str 
    content: str 
    user_id: int 
    owner_id: User | None = None
    @property
    def author(self) -> str | None:
        return self.owner_id.email if self.owner_id else None


