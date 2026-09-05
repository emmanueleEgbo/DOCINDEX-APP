"""auth service is a utility function to hash a password coming from the user.
And another utility to verify if a received password matches the hash stored.
And another one to authenticate and return a user.
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from app.core.config import settings
from app.models.user import User
from app.schemas.user_auth_schema import UserInDB, TokenData
from app.core.database import get_db


password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(plain_password: str) -> str:
    return password_hash.hash(plain_password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


async def get_user(db: AsyncSession, email: str) -> UserInDB | None:

    result = await db.execute(
        select(User).where(
            User.email == email
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        return None

    return UserInDB(
        email=user.email,
        hashed_password=user.hashed_password,
        created_at=user.created_at,
    )


async def authenticate_user(db: AsyncSession, email: str, password: str) -> UserInDB | bool:

    user = await get_user(db, email)
    if not user:
           verify_password(password, DUMMY_HASH)
           return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:

    to_encode = data.copy()
  
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt    

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)], ) -> UserInDB:
        
        credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm],)
            email = payload.get("sub")
            if email is None:
                raise credentials_exception
            
            token_data = TokenData(email=email)

        except InvalidTokenError:
            raise credentials_exception
        
        user = await get_user(db, email=token_data.email)

        if user is None:
            raise credentials_exception
        return user


async def get_current_active_user(current_user: Annotated[UserInDB, Depends(get_current_user)],) -> UserInDB:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user    

