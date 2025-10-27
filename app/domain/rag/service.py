from datetime import datetime
from sqlmodel import Session
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from app.domain.message.models import Message
from app.domain.chat.models import Chat
from app.domain.rag.document_service import DocumentService
from app.domain.rag.embedding_service import EmbeddingService


class RagService:
    """Main orchestrator for the full RAG pipeline (Drive → FAISS → LLM → DB)."""

    def __init__(self, session: Session):
        self.session = session
        self.docs = DocumentService()
        self.embeddings = EmbeddingService()

    def _query(self, db, question: str) -> str:
        """Run the LLM query with FAISS retriever."""
        retriever = db.as_retriever(search_kwargs={"k": 4})
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        qa = RetrievalQA.from_chain_type(
            llm=llm, retriever=retriever, chain_type="stuff"
        )
        result = qa.invoke({"query": question})["result"]
        return result

    def run_pipeline(self, chat_id: int, question: str, file_ids: list[str]):
        """Complete RAG flow with database persistence."""
        # Save user message
        user_msg = Message(
            chat_id=chat_id,
            sender="user",
            content=question,
            created_at=datetime.utcnow(),
        )
        self.session.add(user_msg)
        self.session.commit()
        self.session.refresh(user_msg)

        # Process RAG
        self.docs.download_documents(file_ids)
        db = self.embeddings.create_embeddings(self.docs.docs_path)
        answer = self._query(db, question)

        # Clean temporary data
        self.docs.cleanup()
        self.embeddings.cleanup()

        #  Save bot message
        bot_msg = Message(
            chat_id=chat_id, sender="bot", content=answer, created_at=datetime.utcnow()
        )
        self.session.add(bot_msg)
        self.session.commit()
        self.session.refresh(bot_msg)

        return {"user_message": user_msg, "bot_message": bot_msg}
