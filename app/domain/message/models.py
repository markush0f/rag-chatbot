from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from app.domain.chat.models import Chat


class Message(SQLModel, table=True):
    """Represents an individual message within a chat session."""

    __tablename__ = "message"

    id: Optional[int] = Field(default=None, primary_key=True)
    sender: str = Field(
        nullable=False, description="Indicates the sender (user or bot)"
    )
    content: str = Field(nullable=False, description="Text content of the message")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when the message was created",
    )

    chat_id: int = Field(
        foreign_key="chat.id",
        nullable=False,
        description="Reference to the parent chat session",
    )
    chat: Chat | None = Relationship(back_populates="messages")
