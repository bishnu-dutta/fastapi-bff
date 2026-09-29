from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url : str
    secret_key: SecretStr
    algorithm: str 
    access_token_expire_minutes: int = 60

    MAIL_USERNAME: str 
    MAIL_PASSWORD: str 
    MAIL_FROM: str 
    MAIL_PORT: int 
    MAIL_SERVER: str 
    MAIL_FROM_NAME: str 
    MAIL_STARTTLS: bool =False
    MAIL_SSL_TLS: bool=False
    USE_CREDENTIALS: bool=False
    VALIDATE_CERTS: bool=False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
settings = Settings()