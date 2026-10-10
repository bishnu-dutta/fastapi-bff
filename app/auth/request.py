from pydantic import BaseModel

class UserCredentialsRequest(BaseModel):
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str