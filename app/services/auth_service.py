"""auth service is a utility function to hash a password coming from the user.
And another utility to verify if a received password matches the hash stored.
And another one to authenticate and return a user.
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash