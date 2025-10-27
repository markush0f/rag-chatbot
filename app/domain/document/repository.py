from ast import List
from typing import Sequence, Optional, Any
from sqlmodel import Session, select
from sqlalchemy import func
from .models import Document, DocumentChunk


class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_with_filters(
        self, offset: int = 0, limit: int = 50, filters: dict[str, Any] | None = None
    ) -> Sequence[Document]:
        stmt = select(Document)
        if filters:
            for field, value in filters.items():
                if value is not None and hasattr(Document, field):
                    col = getattr(Document, field)
                    if isinstance(value, str):
                        stmt = stmt.where(col.ilike(f"%{value}%"))
                    else:
                        stmt = stmt.where(col == value)
        stmt = stmt.offset(offset).limit(limit)
        return self.session.exec(stmt).all()

    def count(self) -> int:
        stmt = select(func.count()).select_from(Document)
        return int(self.session.exec(stmt).one())

    def get(self, id: int) -> Optional[Document]:
        return self.session.get(Document, id)

    def create(self, obj: Document) -> Document:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: Document, data: dict) -> Document:
        for key, value in data.items():
            setattr(obj, key, value)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: Document) -> None:
        self.session.delete(obj)
        self.session.commit()

    def get_chunks_by_documents(self, document_ids: list[int]) -> list[DocumentChunk]:
        """
        Retrieve all chunks belonging to the given list of documents.
        Used by ChatService for contextual question answering.
        """
        if not document_ids:
            return []

        stmt = select(DocumentChunk).where(DocumentChunk.document_id.in_(document_ids))
        return self.session.exec(stmt).all()
