from typing import Optional, List
from sqlmodel import SQLModel


class ChatBase(SQLModel):
    title: Optional[str] = None
    document_ids: Optional[List[int]] = None



class ChatCreate(ChatBase):
    user_id: int


class ChatRead(ChatBase):
    id: int
    # user_id: int
    # created_at: str


class ChatPage(SQLModel):
    total: int
    items: List[ChatRead]
