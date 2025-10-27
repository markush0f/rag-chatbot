from typing import List
from sqlmodel import Session
from .models import Message
from .repository import MessageRepository
from .schemas import MessageCreate

class MessageService:
    def __init__(self, session: Session):
        self.repo = MessageRepository(session)

    def list_with_total(self, offset: int, limit: int) -> tuple[list[Message], int]:
        items_seq = self.repo.list(offset=offset, limit=limit)
        items: List[Message] = list(items_seq)
        total = self.repo.count()
        return items, total

    def create(self, data: MessageCreate) -> Message:
        obj = Message.model_validate(data.model_dump())
        return self.repo.create(obj)

    def list_by_chat(self, chat_id: int, offset: int = 0, limit: int = 20) -> tuple[list[Message], int]:
        """Get messages from a paginated chat."""
        items = self.repo.list_by_chat(chat_id, offset=offset, limit=limit)
        total = self.repo.count_by_chat(chat_id)
        return items, total
    
    