from typing import List, Optional, Any
from sqlmodel import Session

from app.domain.rag.embedding_service import EmbeddingService
from app.utils.chunking import split_text_semantic
from app.utils.file_loader import load_text
from .models import Document, DocumentChunk
from .repository import DocumentRepository
from .schemas import DocumentCreate, DocumentUpdate


class DocumentService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = DocumentRepository(session)
        self.embedding_service = EmbeddingService()


    def list_with_total(
        self, offset: int, limit: int, filters: dict[str, Any] | None = None
    ) -> tuple[list[Document], int]:
        items_seq = self.repo.list_with_filters(
            offset=offset, limit=limit, filters=filters
        )
        items: List[Document] = list(items_seq)
        total = self.repo.count()
        return items, total

    def create(self, data: DocumentCreate) -> Document:
        """
        Creates a new document, automatically extracts its content,
        splits it into semantic chunks, and generates embeddings for each chunk.
        """

        # Create and persist the main Document record
        document = Document.model_validate(data.model_dump())
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)

        # Load the raw document content (supports .txt, .pdf, .docx, .md, or URL)
        text = load_text(document.source)

        # Split the content into semantic chunks with overlap
        chunks = split_text_semantic(text, chunk_size=800, overlap=150)

        # Generate embeddings and store each chunk in the database
        for chunk_text in chunks:
            embedding = self.embedding_service.embed_text(chunk_text)
            chunk = DocumentChunk(
                document_id=document.id,
                content=chunk_text,
                embedding=embedding,
            )
            self.session.add(chunk)

        # Commit all inserted chunks and refresh the document
        self.session.commit()
        self.session.refresh(document)

        return document

    def update(self, id: int, data: DocumentUpdate) -> Optional[Document]:
        obj = self.repo.get(id)
        if not obj:
            return None
        return self.repo.update(obj, data.model_dump(exclude_unset=True))

    def delete(self, id: int) -> bool:
        obj = self.repo.get(id)
        if not obj:
            return False
        self.repo.delete(obj)
        return True
