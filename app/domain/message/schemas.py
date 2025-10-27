from typing import List
from sqlmodel import SQLModel


class MessageBase(SQLModel):
    sender: str
    content: str


class MessageCreate(MessageBase):
    chat_id: int


class MessageRead(MessageBase):
    id: int
    chat_id: int
    # created_at: str


class MessagePage(SQLModel):
    total: int
    items: List[MessageRead]
