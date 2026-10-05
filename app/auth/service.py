
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.repository import find_by_keycloak_sub
from app.core.context import org_id_context
from app.models import User
from app.services.keycloak import KeycloakError, decode_access_token, login_user

from .response import TokenResponse

# tokenUrl is used by OpenAPI's "Authorize" button to obtain tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=True)


def get_current_claims(token: str = Depends(oauth2_scheme)) -> dict:
    """Decoded, verified Keycloak token claims: sub, org_id, role, etc."""
    return decode_access_token(token)


async def get_current_auth_user(claims: dict = Depends(get_current_claims)) -> User:
    """Resolves the token's 'sub' to our local Postgres user record."""
    sub = claims.get("sub")
    org_id = claims.get("organization_id")
    user = await find_by_keycloak_sub(sub)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found in local database")
    
    # Using a generator dependency to set the org_id in context ---- we are using org_id from user, I want you take org_id from sub because we have it there 
    context_token = org_id_context.set(org_id)
    try:
        yield user
    finally:
        org_id_context.reset(context_token)

def keycloak_login_user(username:str, password:str):
    try:
        token = login_user(username, password)
        return TokenResponse(**token)
    except KeycloakError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED if e.status_code == 400 else e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


