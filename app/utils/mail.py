import secrets
from datetime import UTC, datetime, timedelta

from fastapi_mail import ConnectionConfig, FastMail

from app.auth.service import hash_password
from app.core.config import settings

mail_config = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_FROM_NAME = settings.MAIL_FROM_NAME,
    MAIL_STARTTLS = settings.MAIL_STARTTLS,
    MAIL_SSL_TLS = settings.MAIL_SSL_TLS,
    USE_CREDENTIALS = settings.USE_CREDENTIALS,
    VALIDATE_CERTS = settings.VALIDATE_CERTS)

mail = FastMail(mail_config)


def generate_otp() -> tuple[str, str]:
    otp = f"{secrets.randbelow(1_000_000):06d}"
    hashed_otp = hash_password(otp)
    return otp, hashed_otp


def get_otp_expiry(minutes: int = 10) -> datetime:
    return datetime.now(UTC) + timedelta(minutes=minutes)


    



