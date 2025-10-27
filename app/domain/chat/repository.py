from typing import List, Sequence
from sqlmodel import Session, select
from sqlalchemy import func
from .models import Chat

class ChatRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self, offset: int = 0, limit: int = 50) -> Sequence[Chat]:
        stmt = select(Chat).offset(offset).limit(limit)
        return self.session.exec(stmt).all()

    def count(self) -> int:
        stmt = select(func.count()).select_from(Chat)
        return int(self.session.exec(stmt).one())

    def create(self, obj: Chat) -> Chat:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj
    
    def get_user_chats(self, user_id: int) -> List[Chat]:
        statement = select(Chat).where(Chat.user_id == user_id)
        results = self.session.exec(statement)
        return results.all()

    def get_by_id(self, chat_id: int) -> Chat | None:
        return self.session.get(Chat, chat_id)