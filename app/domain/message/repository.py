from typing import List, Sequence
from sqlmodel import Session, select
from sqlalchemy import func
from .models import Message

class MessageRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self, offset: int = 0, limit: int = 50) -> Sequence[Message]:
        stmt = select(Message).offset(offset).limit(limit)
        return self.session.exec(stmt).all()

    def count(self) -> int:
        stmt = select(func.count()).select_from(Message)
        return int(self.session.exec(stmt).one())

    def create(self, obj: Message) -> Message:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def list_by_chat(self, chat_id: int, offset: int = 0, limit: int = 20) -> List[Message]:
        """Devuelve mensajes de un chat con paginación."""
        statement = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def count_by_chat(self, chat_id: int) -> int:
        """Cuenta los mensajes totales del chat."""
        statement = select(Message).where(Message.chat_id == chat_id)
        results = self.session.exec(statement)
        return len(results.all())