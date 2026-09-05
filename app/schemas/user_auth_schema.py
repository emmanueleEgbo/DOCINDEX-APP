from pydantic import BaseModel
from datetime import datetime


class CreateUserRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class User(BaseModel):
    email: str
    created_at: datetime

    class ConfigDict:
        from_attributes = True


class UserInDB(User):
    hashed_password: str
