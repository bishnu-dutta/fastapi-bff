
from datetime import datetime

import uuid

from pydantic import EmailStr
from sqlalchemy import func, select

from app.auth.service import hash_password
from app.core.context import get_current_org_id, get_current_session
from app.models import User, UserRole
from app.organizations.request import AdminCreateUserRequest
from .request import CreateUserRequest, UpdateUserRequest


async def save_user_to_database(data: CreateUserRequest | AdminCreateUserRequest, otp_hash: str, otp_expiry: datetime, role: UserRole, organization_id: uuid.UUID) -> User:
    session = get_current_session()
    user = User(
        username=data.username,
        email=data.email.lower(),
        hashed_password=hash_password(data.password),
        otp_hash=otp_hash,
        otp_expiry=otp_expiry,
        otp_attempts=0,
        is_verified=False,
        organization_id=organization_id,
        role=role
    )
    session.add(user)
    await session.commit()
    await session.refresh(user, attribute_names=["organization", "posts"])

    return user

    
async def update_user_otp(user: User,otp_hash: str,otp_expiry: datetime) -> User:
    session = get_current_session()
    user.otp_hash = otp_hash
    user.otp_expiry = otp_expiry
    user.otp_attempts = 0
    await session.commit()
    await session.refresh(user, attribute_names=["organization", "posts"])
    return user


async def find_user_by_email(email:EmailStr) -> User | None:
    session = get_current_session()
    query = select(User).where(func.lower(User.email) == email.lower())
    result = await session.execute(query)
    return result.scalars().first()


async def all_users(offset:int,limit:int) -> list[User]:
    session = get_current_session()
    org_id = get_current_org_id()
    query = select(User).offset(offset).limit(limit).order_by(User.id.asc())
    if org_id:
        query = query.where(User.organization_id == org_id)
    result = await session.execute(query)
    return list(result.scalars().all())


async def find_user_by_id(id: int) -> User | None:
    session = get_current_session()
    org_id = get_current_org_id()
    query = select(User).where(User.id == id)
    if org_id:
        query = query.where(User.organization_id == org_id)
    result = await session.execute(query)
    return result.scalars().first()


async def delete_user_by_id(id: int) -> User | None:
    session = get_current_session()
    user = await find_user_by_id(id)
    if user:
        await session.delete(user)
        await session.commit()
    return user


async def update_user_by_id(id: int, data: UpdateUserRequest) -> User | None:
    session = get_current_session()
    user = await find_user_by_id(id)
    if user:
        if data.username is not None:
            user.username = data.username
        if data.email is not None:
            ''' if find_user_by_email(): return email already used  '''
            user.email = data.email.lower()
        if data.password is not None:
            user.hashed_password = hash_password(data.password)
        await session.commit()
        await session.refresh(user, attribute_names=["organization", "posts"])
    return user

async def update_password_by_email(user_mail: EmailStr, password: str) -> User | None:
    session = get_current_session()
    user_mail.hashed_password = hash_password(password)
    await session.commit()
    await session.refresh(user_mail, attribute_names=["organization", "posts"])
    return user_mail


    
