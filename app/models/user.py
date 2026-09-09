"""
USER ORM model.

Each row in the 'users' table represents a user in our DOCIND system.
A user can either a normal user or admin
"""
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Boolean, DateTime, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class User(Base):
    __tablename__="users"

    id: Mapped[int] = mapped_column(
            Integer,
            primary_key=True,
            autoincrement=True,
        )

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(512), nullable=False) 
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)