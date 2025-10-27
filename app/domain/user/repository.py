from typing import Optional, Sequence
from sqlmodel import Session, select
from sqlalchemy import func
from .models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self, offset: int = 0, limit: int = 50) -> Sequence[User]:
        stmt = select(User).offset(offset).limit(limit)
        return self.session.exec(stmt).all()

    def count(self) -> int:
        stmt = select(func.count()).select_from(User)
        return int(self.session.exec(stmt).one())

    def create(self, obj: User) -> User:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_by_username(self, username: str) -> Optional[User]:
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()

    def get_by_id(self, id: int) -> Optional[User]:
        statement = select(User).where(User.id == id)
        return self.session.exec(statement).first()
