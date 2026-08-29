"""
USER ORM model.

Each row in the 'users' table represents a user in our DOCIND system.
"""
from typing import List
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.core.database import Base


"""
An example user

    "johndoe": {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "password": "password123"
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False, 
    }
"""
class User(Base):
    __tablename__="users"

    id: Mapped[str] = mapped_column(
            Integer,
            primary_key=True,
            autoincrement=True,
        )

    username: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String) 