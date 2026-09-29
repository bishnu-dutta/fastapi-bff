from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.helpers import CurrentUser
from app.users.response import PrivateUserResponse

from .response import Token
from .service import create_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=Token, include_in_schema=False)
async def login_for_access_token(
    # OAuth2PasswordRequstForm -> parses login form data and requires username.
    # oauth2_scheme use this POST /token to return token value from token model
    form_data: OAuth2PasswordRequestForm = Depends()
):
    return await create_token(form_data)


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




