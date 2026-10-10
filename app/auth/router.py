from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.helpers import CurrentUser
from app.auth.service import keycloak_login_user, keycloak_refresh_user_token   
from app.users.response import PrivateUserResponse
from app.auth.request import UserCredentialsRequest, RefreshTokenRequest

from .response import TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=TokenResponse, include_in_schema=False)
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

@router.post("/login", 
                response_model=TokenResponse, 
                status_code=status.HTTP_200_OK, 
                summary="Login user", 
                description="Need user authentication to login user")
async def login_user(
    user_credentials: UserCredentialsRequest
):  
    return keycloak_login_user(user_credentials.username, user_credentials.password)

@router.post("/refresh", 
                response_model=TokenResponse, 
                status_code=status.HTTP_200_OK, 
                summary="Refresh user token", 
                description="Need user authentication to refresh user token")
async def refresh_token(payload: RefreshTokenRequest):
    return keycloak_refresh_user_token(payload.refresh_token)
    

