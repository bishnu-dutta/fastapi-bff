from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI BFF"
    APP_DESCRIPTION: str = "Backend For Frontend (BFF) integrating Keycloak Auth and Directus CMS"
    APP_VERSION: str = "0.1.0"
    DOCS_URL: str | None = "/docs"
    REDOC_URL: str | None = "/redoc"
    OPENAPI_URL: str | None = "/openapi.json"

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

    DIRECTUS_BASE_URL: str 
    DIRECTUS_SERVER_TOKEN: str 
    KEYCLOAK_LOGIN_CLIENT_ID:str
    KEYCLOAK_LOGIN_CLIENT_SECRET:str | None = None
    KEYCLOAK_ADMIN_CLIENT_ID:str
    KEYCLOAK_ADMIN_CLIENT_SECRET:str
    TOKEN_AUDIENCE:str
    KEYCLOAK_SERVER_URL:str
    KEYCLOAK_REALM:str
    KC_HOSTNAME:str
    KC_POSTGRES_USER:str
    KC_POSTGRES_PASSWORD:str
    KC_POSTGRES_DB:str
    KEYCLOAK_ADMIN:str
    KEYCLOAK_ADMIN_PASSWORD:str
    Base_url:str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
settings = Settings()