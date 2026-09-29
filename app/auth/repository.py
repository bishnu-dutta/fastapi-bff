from sqlalchemy import func, select

from app.core.context import get_current_session
from app.models import User


async def find_by_username(username: str) -> User | None:
    session = get_current_session()
    results = await session.execute(
        select(User).where(
            func.lower(User.username) == func.lower(username)
        )
    )
    return results.scalars().first()


async def find_by_email(email:str) -> User | None:
    session = get_current_session()
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalars().first()