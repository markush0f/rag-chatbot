from typing import List
from fastapi import HTTPException
from sqlmodel import Session, select
from openai import OpenAI

from app.core.logging_decorator import log_class_methods
from app.domain.document.models import DocumentChunk
from app.domain.document.repository import DocumentRepository
from app.domain.message.schemas import MessageCreate
from app.domain.message.service import MessageService
from app.domain.rag.embedding_service import EmbeddingService
from app.domain.user.repository import UserRepository
from app.domain.message.models import Message
from app.utils.prompts import rag_prompt
from app.utils.similiraty import cosine_similarity
from .models import Chat
from .repository import ChatRepository
from .schemas import ChatCreate


@log_class_methods("DEBUG")
class ChatService:
    """
    Service layer handling chat creation, message management,
    and RAG question answering over selected documents.
    """

    def __init__(self, session: Session):
        self.session = session
        self.repo = ChatRepository(session)
        self.message_service = MessageService(session)
        self.embedding_service = EmbeddingService()
        self.document_repo = DocumentRepository(session)
        self.client = OpenAI()
        self.model = "gpt-4o-mini"

    def list_with_total(self, offset: int, limit: int) -> tuple[list[Chat], int]:
        items_seq = self.repo.list(offset=offset, limit=limit)
        items: List[Chat] = list(items_seq)
        total = self.repo.count()
        return items, total

    def create(self, data: ChatCreate) -> Chat:
        obj = Chat.model_validate(data.model_dump())
        return self.repo.create(obj)

    def list_by_user(self, user_id: int) -> List[Chat]:
        if not self.user_repo.get_by_id(user_id):
            raise HTTPException(status_code=404, detail="User not found.")
        return self.repo.get_user_chats(user_id)

    def ask(self, chat_id: int, question: str, top_k: int = 5) -> Message:
        """
        Handles a user's question within a chat, retrieves relevant chunks
        from associated documents, and generates a contextual answer.
        """

        # Save the user message
        user_msg = MessageCreate(chat_id=chat_id, sender="user", content=question)
        self.message_service.create(user_msg)

        # Get the chat and its linked documents
        chat = self.repo.get_by_id(chat_id)
        if not chat or not chat.document_ids:
            return self.message_service.create(
                MessageCreate(
                    chat_id=chat_id,
                    sender="assistant",
                    content="No documents are linked to this chat.",
                )
            )

        # Generate embedding for the question
        query_embedding = self.embedding_service.embed_text(question)

        # Retrieve document chunks using document_id
        chunks = self.document_repo.get_chunks_by_documents(chat.document_ids)
        if not chunks:
            return self.message_service.create(
                MessageCreate(
                    chat_id=chat_id,
                    sender="assistant",
                    content="No content found for the selected documents.",
                )
    )

        if not chunks:
            return self.message_service.create(
                MessageCreate(
                    chat_id=chat_id,
                    sender="assistant",
                    content="No content found for the selected documents.",
                )
            )

        # Compute similarity between the question and each chunk
        scored_chunks = [
            (cosine_similarity(query_embedding, c.embedding), c.content)
            for c in chunks
            if c.embedding
        ]
        top_chunks = sorted(scored_chunks, key=lambda x: x[0], reverse=True)[:top_k]
        context = "\n\n".join([chunk for _, chunk in top_chunks])

        # Generate and save assistant's answer
        answer_text = self._generate_answer(question, context)

        chat_msg = MessageCreate(
            chat_id=chat_id, sender="assistant", content=answer_text
        )
        return self.message_service.create(chat_msg)

    def _generate_answer(self, question: str, context: str) -> str:
        """Generate final answer from GPT using contextual information."""
        prompt = rag_prompt(context, question)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
