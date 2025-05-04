"""
SQLAlchemy models for the application's database tables.

This module defines the ORM mappings for the User and Contact entities, using SQLAlchemy's DeclarativeBase system.
"""
from sqlalchemy import Boolean, ForeignKey, Integer, func, String, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.sql.sqltypes import DateTime, Date
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Contact(Base):
    """
    ORM model for a contact record.

    Represents a contact entry belonging to a user, with fields for name, email, phone number, birthday, and optional extra info.
    Enforces a uniqueness constraint on the combination of user ID and email.
    """
    __tablename__ = "contacts"
    __table_args__ = (
        UniqueConstraint("user_id", "email", name="uq_user_email"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String, index=True)
    last_name: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, index=True)
    phone_number: Mapped[str] = mapped_column(String)
    birthday: Mapped[Date] = mapped_column(Date)
    extra_info: Mapped[str] = mapped_column(String, nullable=True)
    user_id: Mapped[int] = mapped_column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")

class User(Base):
    """
    ORM model for a user account.

    Represents an application user with a unique username and email address, hashed password,
    avatar URL, account creation timestamp, and email confirmation status.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
