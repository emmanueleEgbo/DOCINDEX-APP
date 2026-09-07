from pydantic import BaseModel, ConfigDict
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
    # Make Pydantic create the model from an ORM/database object rather than only from a dictionary.
    model_config = ConfigDict(from_attributes=True) 

    email: str
    created_at: datetime
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str
