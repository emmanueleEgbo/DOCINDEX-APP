from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.services.auth_service import get_password_hash
from app.core.database import get_db
from app.models.user import User
from app.schemas.user_auth_schema import CreateUserRequest, UserCreateReturnSchema

router = APIRouter(prefix="/users", tags=['Users'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=User)
def create_user(user: CreateUserRequest, db: Session = Depends(get_db)):
    pass