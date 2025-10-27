from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel


class DocumentBase(SQLModel):
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    owner_id: Optional[int] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentRead(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime


class DocumentUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None


class DocumentPage(SQLModel):
    total: int
    items: List[DocumentRead]
