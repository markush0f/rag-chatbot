from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    """Represents a registered user in the system."""

    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(
        index=True, unique=True, nullable=False, description="Unique username"
    )
    email: str = Field(
        index=True, unique=True, nullable=False, description="User email address"
    )
    full_name: Optional[str] = Field(default=None, description="Full name of the user")
    password: str = Field(nullable=False, description="Hashed password")
    role: str = Field(default="user", description="User role: admin, user, etc.")
    is_active: bool = Field(
        default=True, description="Indicates whether the user is active"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp",
    )

    chats: list["Chat"] = Relationship(back_populates="user")