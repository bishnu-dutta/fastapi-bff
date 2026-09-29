from collections.abc import Sequence

from fastapi import Depends, HTTPException, status

from app.auth.helpers import CurrentUser
from app.models import User, UserRole


class RoleChecker:
    def __init__(self, allowed_roles: Sequence[str | UserRole]):
        self.allowed_roles = set(allowed_roles)

    def __call__(self, current_user: CurrentUser) -> User:
        if current_user.role in self.allowed_roles:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action",
        )


admin = Depends(RoleChecker([UserRole.ORG_ADMIN]))
