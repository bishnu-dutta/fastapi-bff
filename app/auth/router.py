from app.auth.service import keycloak_login_user
from fastapi import HTTPException
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.helpers import CurrentUser
from app.users.response import PrivateUserResponse

from .response import TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    # OAuth2PasswordRequstForm -> parses login form data and requires username.
    # oauth2_scheme use this POST /token to return token value from token model
    form_data: OAuth2PasswordRequestForm = Depends()
):
    return keycloak_login_user(form_data.username, form_data.password)

@router.get("/me", 
            response_model=PrivateUserResponse, 
            status_code=status.HTTP_200_OK, 
            summary="Get current user", 
            description="Need user authentication to get current user data"
            )
async def get_current_user(
    current_user: CurrentUser
):  
    return current_user




