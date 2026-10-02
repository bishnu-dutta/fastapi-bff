
from fastapi import Depends, HTTPException, status

from app.auth.helpers import CurrentUser
from app.auth.service import get_current_claims
from app.models import User, UserRole


class RoleChecker:
    def __init__(self, allowed_role: str | UserRole):
        # Keep allowed roles as strings: {"org_admin", "super_admin"}
        self.allowed_role = allowed_role.value if isinstance(allowed_role, UserRole) else str(allowed_role)
    def __call__(
        self,
        current_user: CurrentUser,
        claims: dict = Depends(get_current_claims),
    ) -> User:
        # Extract the role string directly from the token
        role = claims.get("role")
        # Verify it against allowed roles
        if role != self.allowed_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to perform this action",
            )
        # Return the user so your routes (like current_user: User = admin) keep working
        return current_user

# admin role scope 
admin = Depends(RoleChecker(UserRole.ORG_ADMIN))
